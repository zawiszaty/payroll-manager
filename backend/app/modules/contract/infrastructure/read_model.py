from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contract.infrastructure.models import ContractORM
from app.modules.contract.presentation.views import (
    ContractDetailView,
    ContractListView,
    ContractTermsView,
)


class ContractReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, contract_id: UUID) -> Optional[ContractDetailView]:
        stmt = select(ContractORM).where(ContractORM.id == contract_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return ContractDetailView(
            id=orm.id,
            employee_id=orm.employee_id,
            terms=ContractTermsView(
                contract_type=orm.contract_type,
                rate_amount=orm.rate_amount,
                rate_currency=orm.rate_currency,
                valid_from=orm.valid_from,
                valid_to=orm.valid_to,
                hours_per_week=orm.hours_per_week,
                commission_percentage=orm.commission_percentage,
                description=orm.description,
            ),
            status=orm.status,
            version=orm.version,
            cancellation_reason=orm.cancellation_reason,
            canceled_at=orm.canceled_at,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    async def list(self, skip: int = 0, limit: int = 100) -> Tuple[List[ContractListView], int]:
        # Get total count
        count_stmt = select(func.count()).select_from(ContractORM)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Get paginated items
        stmt = select(ContractORM).offset(skip).limit(limit).order_by(ContractORM.created_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            ContractListView(
                id=orm.id,
                employee_id=orm.employee_id,
                contract_type=orm.contract_type,
                rate_amount=orm.rate_amount,
                rate_currency=orm.rate_currency,
                valid_from=orm.valid_from,
                valid_to=orm.valid_to,
                status=orm.status,
                version=orm.version,
            )
            for orm in orms
        ]

        return items, total_count

    async def get_by_employee(self, employee_id: UUID) -> List[ContractListView]:
        stmt = (
            select(ContractORM)
            .where(ContractORM.employee_id == employee_id)
            .order_by(ContractORM.created_at.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            ContractListView(
                id=orm.id,
                employee_id=orm.employee_id,
                contract_type=orm.contract_type,
                rate_amount=orm.rate_amount,
                rate_currency=orm.rate_currency,
                valid_from=orm.valid_from,
                valid_to=orm.valid_to,
                status=orm.status,
                version=orm.version,
            )
            for orm in orms
        ]

    async def get_active_by_employee(self, employee_id: UUID) -> List[ContractDetailView]:
        from datetime import date

        from app.modules.contract.domain.value_objects import ContractStatus

        today = date.today()
        stmt = (
            select(ContractORM)
            .where(ContractORM.employee_id == employee_id)
            .where(ContractORM.status == ContractStatus.ACTIVE)
            .where(ContractORM.valid_from <= today)
            .where((ContractORM.valid_to.is_(None)) | (ContractORM.valid_to >= today))
            .order_by(ContractORM.valid_from.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            ContractDetailView(
                id=orm.id,
                employee_id=orm.employee_id,
                terms=ContractTermsView(
                    contract_type=orm.contract_type,
                    rate_amount=orm.rate_amount,
                    rate_currency=orm.rate_currency,
                    valid_from=orm.valid_from,
                    valid_to=orm.valid_to,
                    hours_per_week=orm.hours_per_week,
                    commission_percentage=orm.commission_percentage,
                    description=orm.description,
                ),
                status=orm.status,
                version=orm.version,
                cancellation_reason=orm.cancellation_reason,
                canceled_at=orm.canceled_at,
                created_at=orm.created_at.date() if orm.created_at else None,
                updated_at=orm.updated_at.date() if orm.updated_at else None,
            )
            for orm in orms
        ]
