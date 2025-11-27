from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.modules.compensation.domain.models import Bonus, Deduction, Overtime, Rate, SickLeave
from app.modules.compensation.domain.value_objects import (
    BonusType,
    DeductionType,
    OvertimeRule,
    RateType,
    SickLeaveRule,
)
from app.shared.domain.value_objects import DateRange, Money


class CreateRateService:
    def create(
        self,
        employee_id: UUID,
        rate_type: RateType,
        amount: Decimal,
        currency: str,
        valid_from: date,
        valid_to: Optional[date] = None,
        description: Optional[str] = None,
    ) -> Rate:
        return Rate(
            employee_id=employee_id,
            rate_type=rate_type,
            amount=Money(amount=amount, currency=currency),
            date_range=DateRange(valid_from=valid_from, valid_to=valid_to),
            description=description,
        )


class CreateBonusService:
    def create(
        self,
        employee_id: UUID,
        bonus_type: BonusType,
        amount: Decimal,
        currency: str,
        payment_date: date,
        description: Optional[str] = None,
    ) -> Bonus:
        return Bonus(
            employee_id=employee_id,
            bonus_type=bonus_type,
            amount=Money(amount=amount, currency=currency),
            payment_date=payment_date,
            description=description,
        )


class CreateDeductionService:
    def create(
        self,
        employee_id: UUID,
        deduction_type: DeductionType,
        amount: Decimal,
        currency: str,
        valid_from: date,
        valid_to: Optional[date] = None,
        description: Optional[str] = None,
    ) -> Deduction:
        return Deduction(
            employee_id=employee_id,
            deduction_type=deduction_type,
            amount=Money(amount=amount, currency=currency),
            date_range=DateRange(valid_from=valid_from, valid_to=valid_to),
            description=description,
        )


class CreateOvertimeService:
    def create(
        self,
        employee_id: UUID,
        multiplier: Decimal,
        threshold_hours: int,
        valid_from: date,
        valid_to: Optional[date] = None,
    ) -> Overtime:
        rule = OvertimeRule(
            multiplier=multiplier,
            threshold_hours=threshold_hours,
            date_range=DateRange(valid_from=valid_from, valid_to=valid_to),
        )
        return Overtime(employee_id=employee_id, rule=rule)


class CreateSickLeaveService:
    def create(
        self,
        employee_id: UUID,
        percentage: Decimal,
        max_days: Optional[int],
        valid_from: date,
        valid_to: Optional[date] = None,
    ) -> SickLeave:
        rule = SickLeaveRule(
            percentage=percentage,
            max_days=max_days,
            date_range=DateRange(valid_from=valid_from, valid_to=valid_to),
        )
        return SickLeave(employee_id=employee_id, rule=rule)
