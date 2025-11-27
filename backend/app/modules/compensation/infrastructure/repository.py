from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.compensation.domain.models import Bonus, Deduction, Overtime, Rate, SickLeave
from app.modules.compensation.domain.repository import (
    BonusRepository,
    DeductionRepository,
    OvertimeRepository,
    RateRepository,
    SickLeaveRepository,
)
from app.modules.compensation.domain.value_objects import OvertimeRule, SickLeaveRule
from app.modules.compensation.infrastructure.models import (
    BonusORM,
    DeductionORM,
    OvertimeORM,
    RateORM,
    SickLeaveORM,
)
from app.shared.domain.value_objects import DateRange, Money


class SQLAlchemyRateRepository(RateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: RateORM) -> Rate:
        return Rate(
            id=orm.id,
            employee_id=orm.employee_id,
            rate_type=orm.rate_type,
            amount=Money(amount=orm.amount, currency=orm.currency),
            date_range=DateRange(valid_from=orm.valid_from, valid_to=orm.valid_to),
            description=orm.description,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    def _to_orm(self, rate: Rate) -> RateORM:
        return RateORM(
            id=rate.id,
            employee_id=rate.employee_id,
            rate_type=rate.rate_type,
            amount=rate.amount.amount,
            currency=rate.amount.currency,
            valid_from=rate.date_range.valid_from,
            valid_to=rate.date_range.valid_to,
            description=rate.description,
        )

    async def add(self, rate: Rate) -> Rate:
        orm = self._to_orm(rate)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_id(self, rate_id: UUID) -> Optional[Rate]:
        stmt = select(RateORM).where(RateORM.id == rate_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_employee_id(self, employee_id: UUID) -> List[Rate]:
        stmt = select(RateORM).where(RateORM.employee_id == employee_id).order_by(RateORM.valid_from.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def get_active_rate(self, employee_id: UUID, check_date: date) -> Optional[Rate]:
        stmt = (
            select(RateORM)
            .where(
                and_(
                    RateORM.employee_id == employee_id,
                    RateORM.valid_from <= check_date,
                    (RateORM.valid_to.is_(None)) | (RateORM.valid_to >= check_date),
                )
            )
            .order_by(RateORM.valid_from.desc())
        )
        result = await self.session.execute(stmt)
        orm = result.scalars().first()
        return self._to_domain(orm) if orm else None

    async def list(self, skip: int = 0, limit: int = 100) -> List[Rate]:
        stmt = select(RateORM).offset(skip).limit(limit).order_by(RateORM.created_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def update(self, rate: Rate) -> Rate:
        stmt = select(RateORM).where(RateORM.id == rate.id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            raise ValueError(f"Rate {rate.id} not found")

        orm.employee_id = rate.employee_id
        orm.rate_type = rate.rate_type
        orm.amount = rate.amount.amount
        orm.currency = rate.amount.currency
        orm.valid_from = rate.date_range.valid_from
        orm.valid_to = rate.date_range.valid_to
        orm.description = rate.description

        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def delete(self, rate_id: UUID) -> bool:
        stmt = select(RateORM).where(RateORM.id == rate_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return False

        await self.session.delete(orm)
        return True


class SQLAlchemyBonusRepository(BonusRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: BonusORM) -> Bonus:
        return Bonus(
            id=orm.id,
            employee_id=orm.employee_id,
            bonus_type=orm.bonus_type,
            amount=Money(amount=orm.amount, currency=orm.currency),
            payment_date=orm.payment_date,
            description=orm.description,
            created_at=orm.created_at.date() if orm.created_at else None,
        )

    def _to_orm(self, bonus: Bonus) -> BonusORM:
        return BonusORM(
            id=bonus.id,
            employee_id=bonus.employee_id,
            bonus_type=bonus.bonus_type,
            amount=bonus.amount.amount,
            currency=bonus.amount.currency,
            payment_date=bonus.payment_date,
            description=bonus.description,
        )

    async def add(self, bonus: Bonus) -> Bonus:
        orm = self._to_orm(bonus)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_id(self, bonus_id: UUID) -> Optional[Bonus]:
        stmt = select(BonusORM).where(BonusORM.id == bonus_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_employee_id(self, employee_id: UUID) -> List[Bonus]:
        stmt = select(BonusORM).where(BonusORM.employee_id == employee_id).order_by(BonusORM.payment_date.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def list(self, skip: int = 0, limit: int = 100) -> List[Bonus]:
        stmt = select(BonusORM).offset(skip).limit(limit).order_by(BonusORM.created_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def delete(self, bonus_id: UUID) -> bool:
        stmt = select(BonusORM).where(BonusORM.id == bonus_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return False

        await self.session.delete(orm)
        return True


class SQLAlchemyDeductionRepository(DeductionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: DeductionORM) -> Deduction:
        return Deduction(
            id=orm.id,
            employee_id=orm.employee_id,
            deduction_type=orm.deduction_type,
            amount=Money(amount=orm.amount, currency=orm.currency),
            date_range=DateRange(valid_from=orm.valid_from, valid_to=orm.valid_to),
            description=orm.description,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    def _to_orm(self, deduction: Deduction) -> DeductionORM:
        return DeductionORM(
            id=deduction.id,
            employee_id=deduction.employee_id,
            deduction_type=deduction.deduction_type,
            amount=deduction.amount.amount,
            currency=deduction.amount.currency,
            valid_from=deduction.date_range.valid_from,
            valid_to=deduction.date_range.valid_to,
            description=deduction.description,
        )

    async def add(self, deduction: Deduction) -> Deduction:
        orm = self._to_orm(deduction)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_id(self, deduction_id: UUID) -> Optional[Deduction]:
        stmt = select(DeductionORM).where(DeductionORM.id == deduction_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_employee_id(self, employee_id: UUID) -> List[Deduction]:
        stmt = (
            select(DeductionORM).where(DeductionORM.employee_id == employee_id).order_by(DeductionORM.valid_from.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def get_active_deductions(self, employee_id: UUID, check_date: date) -> List[Deduction]:
        stmt = (
            select(DeductionORM)
            .where(
                and_(
                    DeductionORM.employee_id == employee_id,
                    DeductionORM.valid_from <= check_date,
                    (DeductionORM.valid_to.is_(None)) | (DeductionORM.valid_to >= check_date),
                )
            )
            .order_by(DeductionORM.valid_from.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def list(self, skip: int = 0, limit: int = 100) -> List[Deduction]:
        stmt = select(DeductionORM).offset(skip).limit(limit).order_by(DeductionORM.created_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def update(self, deduction: Deduction) -> Deduction:
        stmt = select(DeductionORM).where(DeductionORM.id == deduction.id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            raise ValueError(f"Deduction {deduction.id} not found")

        orm.employee_id = deduction.employee_id
        orm.deduction_type = deduction.deduction_type
        orm.amount = deduction.amount.amount
        orm.currency = deduction.amount.currency
        orm.valid_from = deduction.date_range.valid_from
        orm.valid_to = deduction.date_range.valid_to
        orm.description = deduction.description

        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def delete(self, deduction_id: UUID) -> bool:
        stmt = select(DeductionORM).where(DeductionORM.id == deduction_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return False

        await self.session.delete(orm)
        return True


class SQLAlchemyOvertimeRepository(OvertimeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: OvertimeORM) -> Overtime:
        rule = OvertimeRule(
            multiplier=orm.multiplier,
            threshold_hours=orm.threshold_hours,
            date_range=DateRange(valid_from=orm.valid_from, valid_to=orm.valid_to),
        )
        return Overtime(
            id=orm.id,
            employee_id=orm.employee_id,
            rule=rule,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    def _to_orm(self, overtime: Overtime) -> OvertimeORM:
        return OvertimeORM(
            id=overtime.id,
            employee_id=overtime.employee_id,
            multiplier=overtime.rule.multiplier,
            threshold_hours=overtime.rule.threshold_hours,
            valid_from=overtime.rule.date_range.valid_from,
            valid_to=overtime.rule.date_range.valid_to,
        )

    async def add(self, overtime: Overtime) -> Overtime:
        orm = self._to_orm(overtime)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_id(self, overtime_id: UUID) -> Optional[Overtime]:
        stmt = select(OvertimeORM).where(OvertimeORM.id == overtime_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_employee_id(self, employee_id: UUID) -> List[Overtime]:
        stmt = (
            select(OvertimeORM).where(OvertimeORM.employee_id == employee_id).order_by(OvertimeORM.valid_from.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def update(self, overtime: Overtime) -> Overtime:
        stmt = select(OvertimeORM).where(OvertimeORM.id == overtime.id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            raise ValueError(f"Overtime {overtime.id} not found")

        orm.employee_id = overtime.employee_id
        orm.multiplier = overtime.rule.multiplier
        orm.threshold_hours = overtime.rule.threshold_hours
        orm.valid_from = overtime.rule.date_range.valid_from
        orm.valid_to = overtime.rule.date_range.valid_to

        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def delete(self, overtime_id: UUID) -> bool:
        stmt = select(OvertimeORM).where(OvertimeORM.id == overtime_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return False

        await self.session.delete(orm)
        return True


class SQLAlchemySickLeaveRepository(SickLeaveRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: SickLeaveORM) -> SickLeave:
        rule = SickLeaveRule(
            percentage=orm.percentage,
            max_days=orm.max_days,
            date_range=DateRange(valid_from=orm.valid_from, valid_to=orm.valid_to),
        )
        return SickLeave(
            id=orm.id,
            employee_id=orm.employee_id,
            rule=rule,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    def _to_orm(self, sick_leave: SickLeave) -> SickLeaveORM:
        return SickLeaveORM(
            id=sick_leave.id,
            employee_id=sick_leave.employee_id,
            percentage=sick_leave.rule.percentage,
            max_days=sick_leave.rule.max_days,
            valid_from=sick_leave.rule.date_range.valid_from,
            valid_to=sick_leave.rule.date_range.valid_to,
        )

    async def add(self, sick_leave: SickLeave) -> SickLeave:
        orm = self._to_orm(sick_leave)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_id(self, sick_leave_id: UUID) -> Optional[SickLeave]:
        stmt = select(SickLeaveORM).where(SickLeaveORM.id == sick_leave_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_employee_id(self, employee_id: UUID) -> List[SickLeave]:
        stmt = (
            select(SickLeaveORM)
            .where(SickLeaveORM.employee_id == employee_id)
            .order_by(SickLeaveORM.valid_from.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def update(self, sick_leave: SickLeave) -> SickLeave:
        stmt = select(SickLeaveORM).where(SickLeaveORM.id == sick_leave.id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            raise ValueError(f"SickLeave {sick_leave.id} not found")

        orm.employee_id = sick_leave.employee_id
        orm.percentage = sick_leave.rule.percentage
        orm.max_days = sick_leave.rule.max_days
        orm.valid_from = sick_leave.rule.date_range.valid_from
        orm.valid_to = sick_leave.rule.date_range.valid_to

        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def delete(self, sick_leave_id: UUID) -> bool:
        stmt = select(SickLeaveORM).where(SickLeaveORM.id == sick_leave_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return False

        await self.session.delete(orm)
        return True
