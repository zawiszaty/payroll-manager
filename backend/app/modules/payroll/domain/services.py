"""
Domain services for payroll business logic
These services use Payroll module's internal adapters
"""

from datetime import date
from decimal import Decimal

from app.modules.contract.domain.value_objects import ContractType
from app.modules.payroll.domain.models import Payroll
from app.modules.payroll.domain.value_objects import (
    PayrollDataCollection,
    PayrollLine,
    PayrollLineType,
    PayrollPeriod,
    PayrollPeriodType,
)
from app.modules.payroll.infrastructure.adapters import PayrollDataGatheringAdapter
from app.shared.domain.value_objects import Money


class PayrollCalculationService:
    """
    Service for calculating payroll
    Uses PayrollDataGatheringAdapter which coordinates with internal facades
    """

    def __init__(self, adapter: PayrollDataGatheringAdapter):
        self.adapter = adapter

    async def calculate_payroll(
        self, payroll: Payroll, working_days: int = 22
    ) -> Payroll:
        """
        Calculate payroll for an employee
        Orchestrates the entire payroll calculation process
        """
        # Validate employee eligibility
        can_process = await self.adapter.validate_payroll_eligibility(
            payroll.employee_id, payroll.period.start_date
        )

        if not can_process:
            raise ValueError(
                f"Cannot process payroll for employee {payroll.employee_id} - "
                f"employee not active or no active contract"
            )

        # Gather all data needed via adapter
        payroll_data = await self.adapter.gather_all_payroll_data(
            payroll.employee_id, payroll.period.start_date, payroll.period.end_date
        )

        # Add compensation lines
        await self._add_base_compensation_lines(payroll, payroll_data, working_days)

        # Add bonus lines
        await self._add_bonus_lines(payroll, payroll_data)

        # Add deduction lines
        await self._add_deduction_lines(payroll, payroll_data, working_days)

        # Calculate totals
        payroll.calculate()

        return payroll

    async def _add_base_compensation_lines(
        self, payroll: Payroll, payroll_data: PayrollDataCollection, working_days: int
    ) -> None:
        """Add base salary or hourly wage lines"""
        contract_data = payroll_data.contract_data
        if not contract_data:
            raise ValueError("No active contract found for employee")

        contract_type = contract_data["contract_type"]
        rate_amount = contract_data["rate_amount"]
        contract_id = contract_data["contract_id"]

        # Convert Decimal to Money
        rate_money = Money(rate_amount, "USD")

        if contract_type == ContractType.FIXED_MONTHLY.value:
            # Monthly salary
            line = PayrollLine(
                line_type=PayrollLineType.BASE_SALARY,
                description=f"Base Salary - {payroll.period}",
                quantity=Decimal("1"),
                rate=rate_money,
                amount=rate_money,
                reference_id=contract_id,
            )
            payroll.add_line(line)

        elif contract_type == ContractType.HOURLY.value:
            # Calculate hours based on working days and hours per week
            hours_per_week = contract_data.get("hours_per_week") or Decimal("40")
            # Assuming 5 working days per week
            total_hours = (hours_per_week / Decimal("5")) * Decimal(working_days)

            amount = rate_money * total_hours

            line = PayrollLine(
                line_type=PayrollLineType.HOURLY_WAGE,
                description=f"Hourly Wage - {total_hours} hours @ {rate_money}/hr",
                quantity=total_hours,
                rate=rate_money,
                amount=amount,
                reference_id=contract_id,
            )
            payroll.add_line(line)

    async def _add_bonus_lines(self, payroll: Payroll, payroll_data: PayrollDataCollection) -> None:
        """Add bonus lines from compensation module"""
        bonuses = payroll_data.bonuses

        for bonus in bonuses:
            bonus_amount = Money(bonus.amount, "USD")
            line = PayrollLine(
                line_type=PayrollLineType.BONUS,
                description=f"{bonus.bonus_type.value} - {bonus.description or ''}",
                quantity=Decimal("1"),
                rate=bonus_amount,
                amount=bonus_amount,
                reference_id=bonus.id,
            )
            payroll.add_line(line)

    async def _add_deduction_lines(
        self, payroll: Payroll, payroll_data: PayrollDataCollection, working_days: int
    ) -> None:
        """Add deduction lines for absences"""
        contract_data = payroll_data.contract_data
        absences = payroll_data.absences

        if not absences:
            return

        # Calculate daily rate for deductions
        rate_amount = contract_data["rate_amount"]
        contract_type = contract_data["contract_type"]

        if contract_type == ContractType.FIXED_MONTHLY.value:
            # Monthly salary divided by working days
            daily_rate = Money(rate_amount, "USD") / Decimal(working_days)
        else:
            # For hourly, use hours per day * rate
            hours_per_week = contract_data.get("hours_per_week") or Decimal("40")
            hours_per_day = hours_per_week / Decimal("5")
            daily_rate = Money(rate_amount, "USD") * hours_per_day

        # Calculate deductions via adapter
        absence_impact = await self.adapter.calculate_absence_impact(
            payroll.employee_id,
            payroll.period.start_date,
            payroll.period.end_date,
            daily_rate,
        )

        deduction = absence_impact.deduction_amount
        absence_days = absence_impact.absence_days

        zero_money = Money(Decimal("0"), deduction.currency)
        if deduction > zero_money:
            line = PayrollLine(
                line_type=PayrollLineType.ABSENCE_DEDUCTION,
                description=f"Unpaid Leave Deduction ({absence_days} days)",
                quantity=Decimal(absence_days),
                rate=daily_rate,
                amount=deduction,
            )
            payroll.add_line(line)


class PayrollPeriodService:
    """Service for managing payroll periods"""

    @staticmethod
    def get_monthly_period(year: int, month: int) -> PayrollPeriod:
        """Get monthly payroll period"""
        from calendar import monthrange

        start_date = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        return PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY, start_date=start_date, end_date=end_date
        )

    @staticmethod
    def get_working_days(start_date: date, end_date: date) -> int:
        """Calculate working days in a period (excluding weekends)"""
        working_days = 0
        current_date = start_date

        while current_date <= end_date:
            # Monday = 0, Sunday = 6
            if current_date.weekday() < 5:  # Mon-Fri
                working_days += 1
            current_date = date.fromordinal(current_date.toordinal() + 1)

        return working_days
