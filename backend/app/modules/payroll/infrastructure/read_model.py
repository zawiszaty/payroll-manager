from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.payroll.api.views import (
    PayrollDetailView,
    PayrollLineView,
    PayrollListView,
)
from app.modules.payroll.infrastructure.models import PayrollORM


class PayrollReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, payroll_id: UUID) -> Optional[PayrollDetailView]:
        stmt = (
            select(PayrollORM)
            .options(selectinload(PayrollORM.lines))
            .where(PayrollORM.id == payroll_id)
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return PayrollDetailView(
            id=orm.id,
            employee_id=orm.employee_id,
            period_type=orm.period_type,
            period_start_date=orm.period_start_date,
            period_end_date=orm.period_end_date,
            status=orm.status,
            gross_pay=orm.gross_pay,  # Already Decimal from ORM
            total_deductions=orm.total_deductions,
            total_taxes=orm.total_taxes,
            net_pay=orm.net_pay,
            currency=orm.currency,
            lines=[
                PayrollLineView(
                    line_type=line.line_type,
                    description=line.description,
                    quantity=line.quantity,
                    rate=line.rate,  # Already Decimal from ORM
                    amount=line.amount,
                    currency=line.currency,
                    reference_id=line.reference_id,
                )
                for line in orm.lines
            ],
            approved_by=orm.approved_by,
            approved_at=orm.approved_at,
            processed_at=orm.processed_at,
            paid_at=orm.paid_at,
            payment_reference=orm.payment_reference,
            notes=orm.notes,
            version=orm.version,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    async def list(self, skip: int = 0, limit: int = 100) -> List[PayrollListView]:
        stmt = (
            select(PayrollORM)
            .offset(skip)
            .limit(limit)
            .order_by(PayrollORM.created_at.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            PayrollListView(
                id=orm.id,
                employee_id=orm.employee_id,
                period_type=orm.period_type,
                period_start_date=orm.period_start_date,
                period_end_date=orm.period_end_date,
                status=orm.status,
                gross_pay=orm.gross_pay,
                net_pay=orm.net_pay,
                currency=orm.currency,
                created_at=orm.created_at.date() if orm.created_at else None,
            )
            for orm in orms
        ]

    async def list_by_employee(
        self, employee_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[PayrollListView]:
        stmt = (
            select(PayrollORM)
            .where(PayrollORM.employee_id == employee_id)
            .offset(skip)
            .limit(limit)
            .order_by(PayrollORM.period_start_date.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            PayrollListView(
                id=orm.id,
                employee_id=orm.employee_id,
                period_type=orm.period_type,
                period_start_date=orm.period_start_date,
                period_end_date=orm.period_end_date,
                status=orm.status,
                gross_pay=orm.gross_pay,
                net_pay=orm.net_pay,
                currency=orm.currency,
                created_at=orm.created_at.date() if orm.created_at else None,
            )
            for orm in orms
        ]
