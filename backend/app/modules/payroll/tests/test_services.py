from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.modules.compensation.api.views import BonusView
from app.modules.compensation.domain.value_objects import BonusType
from app.modules.contract.domain.value_objects import ContractType
from app.modules.payroll.domain.models import Payroll
from app.modules.payroll.domain.services import PayrollCalculationService, PayrollPeriodService
from app.modules.payroll.domain.value_objects import (
    AbsenceImpact,
    PayrollDataCollection,
    PayrollLineType,
    PayrollPeriod,
    PayrollPeriodType,
)
from app.modules.payroll.infrastructure.adapters import PayrollDataGatheringAdapter
from app.shared.domain.value_objects import Money


@pytest.fixture
def mock_adapter():
    """Create a mock PayrollDataGatheringAdapter"""
    adapter = Mock(spec=PayrollDataGatheringAdapter)
    adapter.validate_payroll_eligibility = AsyncMock(return_value=True)
    adapter.gather_all_payroll_data = AsyncMock()
    adapter.calculate_absence_impact = AsyncMock()
    return adapter


@pytest.fixture
def payroll_service(mock_adapter):
    """Create PayrollCalculationService with mock adapter"""
    return PayrollCalculationService(mock_adapter)


class TestPayrollCalculationService:
    @pytest.mark.asyncio
    async def test_calculate_payroll_with_fixed_monthly_salary(self, payroll_service, mock_adapter):
        """Test calculating payroll for fixed monthly salary employee"""
        employee_id = uuid4()
        contract_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Setup mock data
        payroll_data = PayrollDataCollection(
            employee=None,
            contract_data={
                "contract_id": contract_id,
                "contract_type": ContractType.FIXED_MONTHLY.value,
                "rate_amount": Decimal("5000.00"),
            },
            bonuses=[],
            absences=[],
        )
        mock_adapter.gather_all_payroll_data.return_value = payroll_data
        mock_adapter.calculate_absence_impact.return_value = AbsenceImpact(
            deduction_amount=Money(Decimal("0"), "USD"), absence_days=0
        )

        # Calculate payroll
        result = await payroll_service.calculate_payroll(payroll, working_days=22)

        # Verify
        assert len(result.lines) == 1
        assert result.lines[0].line_type == PayrollLineType.BASE_SALARY
        assert result.lines[0].amount == Money(Decimal("5000.00"), "USD")
        assert result.summary is not None
        assert result.summary.gross_pay == Money(Decimal("5000.00"), "USD")
        assert result.summary.net_pay == Money(Decimal("5000.00"), "USD")

    @pytest.mark.asyncio
    async def test_calculate_payroll_with_hourly_wage(self, payroll_service, mock_adapter):
        """Test calculating payroll for hourly employee"""
        employee_id = uuid4()
        contract_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Setup mock data - hourly at $25/hr, 40 hrs/week, 22 working days
        payroll_data = PayrollDataCollection(
            employee=None,
            contract_data={
                "contract_id": contract_id,
                "contract_type": ContractType.HOURLY.value,
                "rate_amount": Decimal("25.00"),
                "hours_per_week": Decimal("40"),
            },
            bonuses=[],
            absences=[],
        )
        mock_adapter.gather_all_payroll_data.return_value = payroll_data
        mock_adapter.calculate_absence_impact.return_value = AbsenceImpact(
            deduction_amount=Money(Decimal("0"), "USD"), absence_days=0
        )

        # Calculate payroll
        result = await payroll_service.calculate_payroll(payroll, working_days=22)

        # Verify - 40 hrs/week / 5 days = 8 hrs/day * 22 days = 176 hours
        # 176 * $25 = $4400
        expected_hours = Decimal("176")
        expected_amount = Money(Decimal("4400.00"), "USD")

        assert len(result.lines) == 1
        assert result.lines[0].line_type == PayrollLineType.HOURLY_WAGE
        assert result.lines[0].quantity == expected_hours
        assert result.lines[0].rate == Money(Decimal("25.00"), "USD")
        assert result.lines[0].amount == expected_amount
        assert result.summary.gross_pay == expected_amount

    @pytest.mark.asyncio
    async def test_calculate_payroll_with_bonus(self, payroll_service, mock_adapter):
        """Test calculating payroll with bonuses"""
        employee_id = uuid4()
        contract_id = uuid4()
        bonus_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Setup mock data with bonus
        bonus_view = BonusView(
            id=bonus_id,
            employee_id=employee_id,
            bonus_type=BonusType.PERFORMANCE,
            amount=Decimal("1000.00"),
            currency="USD",
            payment_date=date(2024, 1, 15),
            description="Q4 Performance Bonus",
            created_at=None,
            updated_at=None,
        )

        payroll_data = PayrollDataCollection(
            employee=None,
            contract_data={
                "contract_id": contract_id,
                "contract_type": ContractType.FIXED_MONTHLY.value,
                "rate_amount": Decimal("5000.00"),
            },
            bonuses=[bonus_view],
            absences=[],
        )
        mock_adapter.gather_all_payroll_data.return_value = payroll_data
        mock_adapter.calculate_absence_impact.return_value = AbsenceImpact(
            deduction_amount=Money(Decimal("0"), "USD"), absence_days=0
        )

        # Calculate payroll
        result = await payroll_service.calculate_payroll(payroll, working_days=22)

        # Verify - should have 2 lines (salary + bonus)
        assert len(result.lines) == 2
        assert result.lines[0].line_type == PayrollLineType.BASE_SALARY
        assert result.lines[1].line_type == PayrollLineType.BONUS
        assert result.lines[1].amount == Money(Decimal("1000.00"), "USD")
        assert result.summary.gross_pay == Money(Decimal("6000.00"), "USD")

    @pytest.mark.asyncio
    async def test_calculate_payroll_with_absence_deduction(self, payroll_service, mock_adapter):
        """Test calculating payroll with absence deductions"""
        employee_id = uuid4()
        contract_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Setup mock data
        payroll_data = PayrollDataCollection(
            employee=None,
            contract_data={
                "contract_id": contract_id,
                "contract_type": ContractType.FIXED_MONTHLY.value,
                "rate_amount": Decimal("5000.00"),
            },
            bonuses=[],
            absences=["some_absence"],  # Presence of absence triggers deduction calculation
        )
        mock_adapter.gather_all_payroll_data.return_value = payroll_data

        # Mock absence deduction - 2 days at daily_rate
        # Daily rate = 5000 / 22 = 227.27
        # 2 days = 454.54
        mock_adapter.calculate_absence_impact.return_value = AbsenceImpact(
            deduction_amount=Money(Decimal("454.54"), "USD"), absence_days=2
        )

        # Calculate payroll
        result = await payroll_service.calculate_payroll(payroll, working_days=22)

        # Verify - should have 2 lines (salary + deduction)
        assert len(result.lines) == 2
        assert result.lines[0].line_type == PayrollLineType.BASE_SALARY
        assert result.lines[1].line_type == PayrollLineType.ABSENCE_DEDUCTION
        assert result.lines[1].amount == Money(Decimal("454.54"), "USD")
        assert result.summary.gross_pay == Money(Decimal("5000.00"), "USD")
        assert result.summary.total_deductions == Money(Decimal("454.54"), "USD")
        assert result.summary.net_pay == Money(Decimal("4545.46"), "USD")

    @pytest.mark.asyncio
    async def test_calculate_payroll_complex_scenario(self, payroll_service, mock_adapter):
        """Test calculating payroll with salary, bonus, and deductions"""
        employee_id = uuid4()
        contract_id = uuid4()
        bonus_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Setup complex mock data
        bonus_view = BonusView(
            id=bonus_id,
            employee_id=employee_id,
            bonus_type=BonusType.PERFORMANCE,
            amount=Decimal("1000.00"),
            currency="USD",
            payment_date=date(2024, 1, 15),
            description="Performance Bonus",
            created_at=None,
            updated_at=None,
        )

        payroll_data = PayrollDataCollection(
            employee=None,
            contract_data={
                "contract_id": contract_id,
                "contract_type": ContractType.FIXED_MONTHLY.value,
                "rate_amount": Decimal("5000.00"),
            },
            bonuses=[bonus_view],
            absences=["absence"],
        )
        mock_adapter.gather_all_payroll_data.return_value = payroll_data
        mock_adapter.calculate_absence_impact.return_value = AbsenceImpact(
            deduction_amount=Money(Decimal("454.54"), "USD"), absence_days=2
        )

        # Calculate payroll
        result = await payroll_service.calculate_payroll(payroll, working_days=22)

        # Verify complex calculation
        # Gross = 5000 + 1000 = 6000
        # Deductions = 454.54
        # Net = 6000 - 454.54 = 5545.46
        assert len(result.lines) == 3
        assert result.summary.gross_pay == Money(Decimal("6000.00"), "USD")
        assert result.summary.total_deductions == Money(Decimal("454.54"), "USD")
        assert result.summary.net_pay == Money(Decimal("5545.46"), "USD")

    @pytest.mark.asyncio
    async def test_calculate_payroll_ineligible_employee(self, payroll_service, mock_adapter):
        """Test that ineligible employee raises error"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Setup mock to return ineligible
        mock_adapter.validate_payroll_eligibility.return_value = False

        # Should raise error
        with pytest.raises(ValueError, match="Cannot process payroll"):
            await payroll_service.calculate_payroll(payroll, working_days=22)

    @pytest.mark.asyncio
    async def test_calculate_payroll_no_contract(self, payroll_service, mock_adapter):
        """Test that missing contract raises error"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Setup mock data with empty contract (which will be None when checked)
        payroll_data = PayrollDataCollection(
            employee=None, contract_data={}, bonuses=[], absences=[]
        )
        mock_adapter.gather_all_payroll_data.return_value = payroll_data

        # Should raise error when service checks contract_data
        with pytest.raises(ValueError, match="No active contract found"):
            await payroll_service.calculate_payroll(payroll, working_days=22)

    @pytest.mark.asyncio
    async def test_calculate_payroll_no_deduction_for_zero_absence(
        self, payroll_service, mock_adapter
    ):
        """Test that zero absence days does not add deduction line"""
        employee_id = uuid4()
        contract_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Setup mock data with absences but zero deduction
        payroll_data = PayrollDataCollection(
            employee=None,
            contract_data={
                "contract_id": contract_id,
                "contract_type": ContractType.FIXED_MONTHLY.value,
                "rate_amount": Decimal("5000.00"),
            },
            bonuses=[],
            absences=["absence"],  # Has absences but all paid
        )
        mock_adapter.gather_all_payroll_data.return_value = payroll_data
        mock_adapter.calculate_absence_impact.return_value = AbsenceImpact(
            deduction_amount=Money(Decimal("0"), "USD"), absence_days=0
        )

        # Calculate payroll
        result = await payroll_service.calculate_payroll(payroll, working_days=22)

        # Should only have salary line, no deduction
        assert len(result.lines) == 1
        assert result.lines[0].line_type == PayrollLineType.BASE_SALARY

    @pytest.mark.asyncio
    async def test_calculate_payroll_hourly_with_deduction(self, payroll_service, mock_adapter):
        """Test calculating payroll for hourly employee with deductions"""
        employee_id = uuid4()
        contract_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Setup mock data - hourly employee
        payroll_data = PayrollDataCollection(
            employee=None,
            contract_data={
                "contract_id": contract_id,
                "contract_type": ContractType.HOURLY.value,
                "rate_amount": Decimal("25.00"),
                "hours_per_week": Decimal("40"),
            },
            bonuses=[],
            absences=["absence"],
        )
        mock_adapter.gather_all_payroll_data.return_value = payroll_data

        # Mock deduction - hourly deduction calculated differently
        # Daily rate = 25 * 8 (hours_per_day) = 200
        # 1 day = 200
        mock_adapter.calculate_absence_impact.return_value = AbsenceImpact(
            deduction_amount=Money(Decimal("200.00"), "USD"), absence_days=1
        )

        # Calculate payroll
        result = await payroll_service.calculate_payroll(payroll, working_days=22)

        # Verify
        assert len(result.lines) == 2
        assert result.lines[0].line_type == PayrollLineType.HOURLY_WAGE
        assert result.lines[1].line_type == PayrollLineType.ABSENCE_DEDUCTION
        assert result.summary.total_deductions == Money(Decimal("200.00"), "USD")


class TestPayrollPeriodService:
    def test_get_monthly_period(self):
        """Test getting monthly payroll period"""
        period = PayrollPeriodService.get_monthly_period(2024, 1)

        assert period.period_type == PayrollPeriodType.MONTHLY
        assert period.start_date == date(2024, 1, 1)
        assert period.end_date == date(2024, 1, 31)

    def test_get_monthly_period_february_leap_year(self):
        """Test February in leap year"""
        period = PayrollPeriodService.get_monthly_period(2024, 2)

        assert period.start_date == date(2024, 2, 1)
        assert period.end_date == date(2024, 2, 29)

    def test_get_monthly_period_february_non_leap_year(self):
        """Test February in non-leap year"""
        period = PayrollPeriodService.get_monthly_period(2023, 2)

        assert period.start_date == date(2023, 2, 1)
        assert period.end_date == date(2023, 2, 28)

    def test_get_working_days_full_week(self):
        """Test calculating working days for a full week"""
        # Monday to Friday
        working_days = PayrollPeriodService.get_working_days(date(2024, 1, 1), date(2024, 1, 5))

        assert working_days == 5

    def test_get_working_days_with_weekend(self):
        """Test calculating working days including weekend"""
        # Monday to Sunday (should count 5 days)
        working_days = PayrollPeriodService.get_working_days(date(2024, 1, 1), date(2024, 1, 7))

        assert working_days == 5

    def test_get_working_days_full_month(self):
        """Test calculating working days for a full month"""
        # January 2024 - 31 days
        # Need to check actual working days
        working_days = PayrollPeriodService.get_working_days(date(2024, 1, 1), date(2024, 1, 31))

        # January 2024 starts on Monday and has 31 days
        # 4 full weeks (20 days) + 3 more weekdays = 23 working days
        assert working_days == 23

    def test_get_working_days_single_day_weekday(self):
        """Test calculating working days for single weekday"""
        # Monday
        working_days = PayrollPeriodService.get_working_days(date(2024, 1, 1), date(2024, 1, 1))

        assert working_days == 1

    def test_get_working_days_single_day_weekend(self):
        """Test calculating working days for single weekend day"""
        # Saturday
        working_days = PayrollPeriodService.get_working_days(date(2024, 1, 6), date(2024, 1, 6))

        assert working_days == 0

    def test_get_working_days_weekend_only(self):
        """Test calculating working days for weekend only"""
        # Saturday to Sunday
        working_days = PayrollPeriodService.get_working_days(date(2024, 1, 6), date(2024, 1, 7))

        assert working_days == 0
