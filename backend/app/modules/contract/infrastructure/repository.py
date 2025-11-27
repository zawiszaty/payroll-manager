from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contract.domain.models import Contract
from app.modules.contract.domain.repository import ContractRepository
from app.modules.contract.domain.value_objects import ContractStatus, ContractTerms
from app.modules.contract.infrastructure.models import ContractORM
from app.shared.domain.value_objects import DateRange, Money


class SQLAlchemyContractRepository(ContractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

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

    async def add(self, contract: Contract) -> Contract:
        orm = self._to_orm(contract)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_id(self, contract_id: UUID) -> Optional[Contract]:
        stmt = select(ContractORM).where(ContractORM.id == contract_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_employee_id(self, employee_id: UUID) -> List[Contract]:
        stmt = select(ContractORM).where(ContractORM.employee_id == employee_id).order_by(ContractORM.created_at.desc())
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

    async def update(self, contract: Contract) -> Contract:
        stmt = select(ContractORM).where(ContractORM.id == contract.id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            raise ValueError(f"Contract {contract.id} not found")

        orm.employee_id = contract.employee_id
        orm.contract_type = contract.terms.contract_type
        orm.status = contract.status
        orm.version = contract.version
        orm.rate_amount = contract.terms.rate.amount
        orm.rate_currency = contract.terms.rate.currency
        orm.valid_from = contract.terms.date_range.valid_from
        orm.valid_to = contract.terms.date_range.valid_to
        orm.hours_per_week = contract.terms.hours_per_week
        orm.commission_percentage = contract.terms.commission_percentage
        orm.description = contract.terms.description
        orm.cancellation_reason = contract.cancellation_reason
        orm.canceled_at = contract.canceled_at

        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def delete(self, contract_id: UUID) -> bool:
        stmt = select(ContractORM).where(ContractORM.id == contract_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return False

        await self.session.delete(orm)
        return True
