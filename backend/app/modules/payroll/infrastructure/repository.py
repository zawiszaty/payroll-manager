"""
SQLAlchemy implementation of PayrollRepository
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.payroll.domain.models import Payroll
from app.modules.payroll.domain.repository import PayrollRepository
from app.modules.payroll.domain.value_objects import PayrollLine, PayrollPeriod, PayrollSummary
from app.modules.payroll.infrastructure.models import PayrollLineORM, PayrollORM
from app.shared.domain.value_objects import Money


class SQLAlchemyPayrollRepository(PayrollRepository):
    """SQLAlchemy implementation of PayrollRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: PayrollORM) -> Payroll:
        """Convert ORM model to domain model"""
        period = PayrollPeriod(
            period_type=orm.period_type,
            start_date=orm.period_start_date,
            end_date=orm.period_end_date,
        )

        lines = [
            PayrollLine(
                line_type=line_orm.line_type,
                description=line_orm.description,
                quantity=line_orm.quantity,
                rate=Money(line_orm.rate, line_orm.currency),
                amount=Money(line_orm.amount, line_orm.currency),
                reference_id=line_orm.reference_id,
            )
            for line_orm in orm.lines
        ]

        # Create summary if we have calculated values
        summary = None
        if orm.gross_pay is not None:
            summary = PayrollSummary(
                gross_pay=Money(orm.gross_pay, orm.currency),
                total_deductions=Money(orm.total_deductions, orm.currency),
                total_taxes=Money(orm.total_taxes, orm.currency),
                net_pay=Money(orm.net_pay, orm.currency),
            )

        payroll = Payroll(
            payroll_id=orm.id,
            employee_id=orm.employee_id,
            period=period,
            status=orm.status,
            lines=lines,
            summary=summary,
            notes=orm.notes,
            approved_by=orm.approved_by,
            approved_at=orm.approved_at,
            processed_at=orm.processed_at,
            paid_at=orm.paid_at,
            payment_reference=orm.payment_reference,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

        return payroll

    def _to_orm(self, payroll: Payroll) -> PayrollORM:
        """Convert domain model to ORM model"""
        # Extract summary values if available
        gross_pay = payroll.summary.gross_pay.amount if payroll.summary else 0
        total_deductions = payroll.summary.total_deductions.amount if payroll.summary else 0
        total_taxes = payroll.summary.total_taxes.amount if payroll.summary else 0
        net_pay = payroll.summary.net_pay.amount if payroll.summary else 0
        currency = payroll.summary.gross_pay.currency if payroll.summary else "USD"

        orm = PayrollORM(
            id=payroll.id,
            employee_id=payroll.employee_id,
            period_type=payroll.period.period_type,
            period_start_date=payroll.period.start_date,
            period_end_date=payroll.period.end_date,
            status=payroll.status,
            gross_pay=gross_pay,
            total_deductions=total_deductions,
            total_taxes=total_taxes,
            net_pay=net_pay,
            currency=currency,
            approved_by=payroll.approved_by,
            approved_at=payroll.approved_at,
            processed_at=payroll.processed_at,
            paid_at=payroll.paid_at,
            payment_reference=payroll.payment_reference,
            notes=payroll.notes,
            version="1",
        )

        orm.lines = [
            PayrollLineORM(
                line_type=line.line_type,
                description=line.description,
                quantity=line.quantity,
                rate=line.rate.amount,
                amount=line.amount.amount,
                currency=line.amount.currency,
                reference_id=line.reference_id,
            )
            for line in payroll.lines
        ]

        return orm

    async def save(self, payroll: Payroll) -> Payroll:
        """Save payroll (insert or update using merge)"""
        orm = self._to_orm(payroll)
        merged_orm = await self.session.merge(orm)
        await self.session.flush()

        # Re-query with eager loading to avoid lazy load issues
        stmt = (
            select(PayrollORM)
            .options(selectinload(PayrollORM.lines))
            .where(PayrollORM.id == merged_orm.id)
        )
        result = await self.session.execute(stmt)
        refreshed_orm = result.scalar_one()

        return self._to_domain(refreshed_orm)

    async def get_by_id(self, payroll_id: UUID) -> Optional[Payroll]:
        """Get payroll by ID"""
        stmt = (
            select(PayrollORM)
            .options(selectinload(PayrollORM.lines))
            .where(PayrollORM.id == payroll_id)
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def find_by_employee(
        self, employee_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Payroll]:
        """Find payrolls by employee"""
        stmt = (
            select(PayrollORM)
            .options(selectinload(PayrollORM.lines))
            .where(PayrollORM.employee_id == employee_id)
            .order_by(PayrollORM.period_start_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Payroll]:
        """Find all payrolls"""
        stmt = (
            select(PayrollORM)
            .options(selectinload(PayrollORM.lines))
            .order_by(PayrollORM.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def get_by_employee(self, employee_id: UUID) -> List[Payroll]:
        """Get all payrolls for an employee - wrapper around find_by_employee"""
        return await self.find_by_employee(employee_id)

    async def delete(self, payroll_id: UUID) -> None:
        """Delete a payroll"""
        stmt = select(PayrollORM).where(PayrollORM.id == payroll_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm:
            await self.session.delete(orm)
            await self.session.flush()
