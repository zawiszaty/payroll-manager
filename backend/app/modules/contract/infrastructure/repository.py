import logging
from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contract.domain.models import Contract
from app.modules.contract.domain.repository import ContractRepository
from app.modules.contract.domain.value_objects import ContractStatus, ContractTerms
from app.modules.contract.infrastructure.models import ContractORM
from app.shared.domain.events import get_event_dispatcher
from app.shared.domain.value_objects import DateRange, Money

logger = logging.getLogger(__name__)


class SQLAlchemyContractRepository(ContractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.event_dispatcher = get_event_dispatcher()

    async def _dispatch_events(self, contract: Contract, event_type: str) -> None:
        """
        Dispatch contract events based on the operation type.
        Errors are logged but don't prevent the operation from succeeding.
        """
        from app.modules.contract.domain.events import (
            ContractActivatedEvent,
            ContractCanceledEvent,
            ContractCreatedEvent,
            ContractExpiredEvent,
        )

        try:
            event = None

            if event_type == "created":
                event = ContractCreatedEvent(
                    contract_id=contract.id,
                    employee_id=contract.employee_id,
                    contract_type=contract.terms.contract_type.value if contract.terms else "",
                    rate_amount=contract.terms.rate.amount if contract.terms else 0,
                    rate_currency=contract.terms.rate.currency if contract.terms else "USD",
                    valid_from=contract.terms.date_range.valid_from
                    if contract.terms
                    else date.today(),
                    valid_to=contract.terms.date_range.valid_to if contract.terms else None,
                )
            elif event_type == "activated":
                event = ContractActivatedEvent(
                    contract_id=contract.id,
                    employee_id=contract.employee_id,
                    contract_type=contract.terms.contract_type.value if contract.terms else "",
                    activated_at=contract.updated_at,
                )
            elif event_type == "canceled":
                event = ContractCanceledEvent(
                    contract_id=contract.id,
                    employee_id=contract.employee_id,
                    contract_type=contract.terms.contract_type.value if contract.terms else "",
                    cancellation_reason=contract.cancellation_reason or "",
                    canceled_at=contract.canceled_at or date.today(),
                )
            elif event_type == "expired":
                event = ContractExpiredEvent(
                    contract_id=contract.id,
                    employee_id=contract.employee_id,
                    contract_type=contract.terms.contract_type.value if contract.terms else "",
                    expired_at=contract.updated_at,
                )

            if event:
                await self.event_dispatcher.dispatch(event)
                logger.debug(f"Successfully dispatched event: {event.__class__.__name__}")
        except Exception as e:
            # Log the error with context but don't fail the entire operation
            logger.error(
                f"Failed to dispatch {event_type} event for contract {contract.id}: {e}",
                exc_info=True,
            )

    def _to_domain(self, orm: ContractORM) -> Contract:
        terms = ContractTerms(
            contract_type=orm.contract_type,
            rate=Money(amount=orm.rate_amount, currency=orm.rate_currency),
            date_range=DateRange(valid_from=orm.valid_from, valid_to=orm.valid_to),
            hours_per_week=orm.hours_per_week,
            commission_percentage=orm.commission_percentage,
            description=orm.description,
        )

        return Contract(
            id=orm.id,
            employee_id=orm.employee_id,
            terms=terms,
            status=orm.status,
            version=orm.version,
            cancellation_reason=orm.cancellation_reason,
            canceled_at=orm.canceled_at,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    def _to_orm(self, contract: Contract) -> ContractORM:
        return ContractORM(
            id=contract.id,
            employee_id=contract.employee_id,
            contract_type=contract.terms.contract_type,
            status=contract.status,
            version=contract.version,
            rate_amount=contract.terms.rate.amount,
            rate_currency=contract.terms.rate.currency,
            valid_from=contract.terms.date_range.valid_from,
            valid_to=contract.terms.date_range.valid_to,
            hours_per_week=contract.terms.hours_per_week,
            commission_percentage=contract.terms.commission_percentage,
            description=contract.terms.description,
            cancellation_reason=contract.cancellation_reason,
            canceled_at=contract.canceled_at,
        )

    async def save(self, contract: Contract, event_type: str | None = None) -> Contract:
        """Save a contract to the database (add or update)."""
        orm = self._to_orm(contract)
        merged_orm = await self.session.merge(orm)
        await self.session.flush()

        # Dispatch event if event_type is provided
        if event_type:
            await self._dispatch_events(contract, event_type)

        await self.session.refresh(merged_orm)
        return self._to_domain(merged_orm)

    async def get_by_id(self, contract_id: UUID) -> Optional[Contract]:
        stmt = select(ContractORM).where(ContractORM.id == contract_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_employee_id(self, employee_id: UUID) -> List[Contract]:
        stmt = (
            select(ContractORM)
            .where(ContractORM.employee_id == employee_id)
            .order_by(ContractORM.created_at.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def get_active_contracts(self, employee_id: UUID) -> List[Contract]:
        stmt = (
            select(ContractORM)
            .where(ContractORM.employee_id == employee_id)
            .where(ContractORM.status == ContractStatus.ACTIVE)
            .order_by(ContractORM.created_at.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def list(self, skip: int = 0, limit: int = 100) -> List[Contract]:
        stmt = select(ContractORM).offset(skip).limit(limit).order_by(ContractORM.created_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def delete(self, contract_id: UUID) -> bool:
        stmt = select(ContractORM).where(ContractORM.id == contract_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return False

        await self.session.delete(orm)
        return True

    async def get_expired_contracts(self, check_date: date) -> List[Contract]:
        """Get all ACTIVE contracts where valid_to < check_date"""
        stmt = (
            select(ContractORM)
            .where(ContractORM.status == ContractStatus.ACTIVE)
            .where(ContractORM.valid_to.isnot(None))
            .where(ContractORM.valid_to < check_date)
            .order_by(ContractORM.valid_to)
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]
