from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from app.modules.payroll.domain.models import Payroll
from app.modules.payroll.domain.value_objects import (
    PayrollLine,
    PayrollLineType,
    PayrollPeriod,
    PayrollPeriodType,
    PayrollStatus,
)
from app.shared.domain.value_objects import Money


class TestPayrollCreation:
    def test_create_payroll(self):
        """Test creating a new payroll"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        payroll = Payroll.create(employee_id=employee_id, period=period, notes="Test payroll")

        assert payroll.employee_id == employee_id
        assert payroll.period == period
        assert payroll.status == PayrollStatus.DRAFT
        assert payroll.notes == "Test payroll"
        assert len(payroll.lines) == 0
        assert payroll.summary is None
        assert len(payroll.get_domain_events()) == 1

    def test_create_payroll_generates_id(self):
        """Test that creating a payroll generates a unique ID"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        payroll = Payroll.create(employee_id=employee_id, period=period)

        assert payroll.id is not None


class TestPayrollLines:
    def test_add_line_to_draft_payroll(self):
        """Test adding a line to a draft payroll"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )

        payroll.add_line(line)

        assert len(payroll.lines) == 1
        assert payroll.lines[0] == line

    def test_add_line_to_pending_approval_payroll(self):
        """Test adding a line to a payroll pending approval"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Add line and calculate
        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(line)
        payroll.calculate()
        payroll.submit_for_approval()

        # Should be able to add line in PENDING_APPROVAL status
        bonus_line = PayrollLine(
            line_type=PayrollLineType.BONUS,
            description="Performance Bonus",
            quantity=Decimal("1"),
            rate=Money(Decimal("1000.00"), "USD"),
            amount=Money(Decimal("1000.00"), "USD"),
        )
        payroll.add_line(bonus_line)

        assert len(payroll.lines) == 2

    def test_cannot_add_line_to_approved_payroll(self):
        """Test that lines cannot be added to approved payroll"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Add line, calculate, submit, and approve
        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(line)
        payroll.calculate()
        payroll.submit_for_approval()
        payroll.approve(uuid4())

        # Try to add another line
        bonus_line = PayrollLine(
            line_type=PayrollLineType.BONUS,
            description="Bonus",
            quantity=Decimal("1"),
            rate=Money(Decimal("1000.00"), "USD"),
            amount=Money(Decimal("1000.00"), "USD"),
        )

        with pytest.raises(ValueError, match="Cannot add lines to payroll in"):
            payroll.add_line(bonus_line)


class TestPayrollCalculation:
    def test_calculate_simple_salary(self):
        """Test calculating payroll with simple base salary"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(line)
        payroll.calculate()

        assert payroll.summary is not None
        assert payroll.summary.gross_pay == Money(Decimal("5000.00"), "USD")
        assert payroll.summary.total_deductions == Money(Decimal("0.00"), "USD")
        assert payroll.summary.total_taxes == Money(Decimal("0.00"), "USD")
        assert payroll.summary.net_pay == Money(Decimal("5000.00"), "USD")

    def test_calculate_with_deductions(self):
        """Test calculating payroll with deductions"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Add salary line
        salary_line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(salary_line)

        # Add deduction line
        deduction_line = PayrollLine(
            line_type=PayrollLineType.DEDUCTION,
            description="Health Insurance",
            quantity=Decimal("1"),
            rate=Money(Decimal("200.00"), "USD"),
            amount=Money(Decimal("200.00"), "USD"),
        )
        payroll.add_line(deduction_line)

        payroll.calculate()

        assert payroll.summary.gross_pay == Money(Decimal("5000.00"), "USD")
        assert payroll.summary.total_deductions == Money(Decimal("200.00"), "USD")
        assert payroll.summary.total_taxes == Money(Decimal("0.00"), "USD")
        assert payroll.summary.net_pay == Money(Decimal("4800.00"), "USD")

    def test_calculate_with_taxes(self):
        """Test calculating payroll with taxes"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Add salary line
        salary_line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(salary_line)

        # Add tax line
        tax_line = PayrollLine(
            line_type=PayrollLineType.TAX,
            description="Federal Tax",
            quantity=Decimal("1"),
            rate=Money(Decimal("750.00"), "USD"),
            amount=Money(Decimal("750.00"), "USD"),
        )
        payroll.add_line(tax_line)

        payroll.calculate()

        assert payroll.summary.gross_pay == Money(Decimal("5000.00"), "USD")
        assert payroll.summary.total_deductions == Money(Decimal("0.00"), "USD")
        assert payroll.summary.total_taxes == Money(Decimal("750.00"), "USD")
        assert payroll.summary.net_pay == Money(Decimal("4250.00"), "USD")

    def test_calculate_complex_payroll(self):
        """Test calculating payroll with multiple line types"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Base salary
        payroll.add_line(
            PayrollLine(
                line_type=PayrollLineType.BASE_SALARY,
                description="Base Salary",
                quantity=Decimal("1"),
                rate=Money(Decimal("5000.00"), "USD"),
                amount=Money(Decimal("5000.00"), "USD"),
            )
        )

        # Bonus
        payroll.add_line(
            PayrollLine(
                line_type=PayrollLineType.BONUS,
                description="Performance Bonus",
                quantity=Decimal("1"),
                rate=Money(Decimal("1000.00"), "USD"),
                amount=Money(Decimal("1000.00"), "USD"),
            )
        )

        # Overtime
        payroll.add_line(
            PayrollLine(
                line_type=PayrollLineType.OVERTIME,
                description="Overtime Hours",
                quantity=Decimal("10"),
                rate=Money(Decimal("50.00"), "USD"),
                amount=Money(Decimal("500.00"), "USD"),
            )
        )

        # Deduction
        payroll.add_line(
            PayrollLine(
                line_type=PayrollLineType.DEDUCTION,
                description="Health Insurance",
                quantity=Decimal("1"),
                rate=Money(Decimal("200.00"), "USD"),
                amount=Money(Decimal("200.00"), "USD"),
            )
        )

        # Tax
        payroll.add_line(
            PayrollLine(
                line_type=PayrollLineType.TAX,
                description="Federal Tax",
                quantity=Decimal("1"),
                rate=Money(Decimal("975.00"), "USD"),
                amount=Money(Decimal("975.00"), "USD"),
            )
        )

        payroll.calculate()

        # Gross = 5000 + 1000 + 500 = 6500
        # Deductions = 200
        # Taxes = 975
        # Net = 6500 - 200 - 975 = 5325
        assert payroll.summary.gross_pay == Money(Decimal("6500.00"), "USD")
        assert payroll.summary.total_deductions == Money(Decimal("200.00"), "USD")
        assert payroll.summary.total_taxes == Money(Decimal("975.00"), "USD")
        assert payroll.summary.net_pay == Money(Decimal("5325.00"), "USD")

    def test_cannot_calculate_without_lines(self):
        """Test that calculation fails without line items"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        with pytest.raises(ValueError, match="Cannot calculate payroll without line items"):
            payroll.calculate()

    def test_calculate_generates_event(self):
        """Test that calculation generates a domain event"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(line)

        # Clear creation event
        payroll.clear_domain_events()

        payroll.calculate()

        events = payroll.get_domain_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "PayrollCalculatedEvent"


class TestPayrollWorkflow:
    def test_submit_for_approval(self):
        """Test submitting payroll for approval"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Add line and calculate
        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(line)
        payroll.calculate()

        payroll.submit_for_approval()

        assert payroll.status == PayrollStatus.PENDING_APPROVAL

    def test_cannot_submit_uncalculated_payroll(self):
        """Test that uncalculated payroll cannot be submitted"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        with pytest.raises(ValueError, match="Payroll must be calculated before submission"):
            payroll.submit_for_approval()

    def test_approve_payroll(self):
        """Test approving a payroll"""
        employee_id = uuid4()
        approver_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Add line, calculate, and submit
        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(line)
        payroll.calculate()
        payroll.submit_for_approval()

        payroll.approve(approver_id)

        assert payroll.status == PayrollStatus.APPROVED
        assert payroll.approved_by == approver_id
        assert payroll.approved_at is not None

    def test_cannot_approve_draft_payroll(self):
        """Test that draft payroll cannot be approved"""
        employee_id = uuid4()
        approver_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        with pytest.raises(ValueError, match="Cannot approve payroll in"):
            payroll.approve(approver_id)

    def test_process_payroll(self):
        """Test processing an approved payroll"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Add line, calculate, submit, and approve
        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(line)
        payroll.calculate()
        payroll.submit_for_approval()
        payroll.approve(uuid4())

        payroll.process()

        assert payroll.status == PayrollStatus.PROCESSED
        assert payroll.processed_at is not None

    def test_mark_as_paid(self):
        """Test marking a processed payroll as paid"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Add line, calculate, submit, approve, and process
        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(line)
        payroll.calculate()
        payroll.submit_for_approval()
        payroll.approve(uuid4())
        payroll.process()

        payment_ref = "PAY-2024-001"
        payroll.mark_as_paid(payment_ref)

        assert payroll.status == PayrollStatus.PAID
        assert payroll.payment_reference == payment_ref
        assert payroll.paid_at is not None

    def test_cancel_draft_payroll(self):
        """Test cancelling a draft payroll"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        payroll.cancel()

        assert payroll.status == PayrollStatus.CANCELLED

    def test_cannot_cancel_processed_payroll(self):
        """Test that processed payroll cannot be cancelled"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        # Add line, calculate, submit, approve, and process
        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "USD"),
            amount=Money(Decimal("5000.00"), "USD"),
        )
        payroll.add_line(line)
        payroll.calculate()
        payroll.submit_for_approval()
        payroll.approve(uuid4())
        payroll.process()

        with pytest.raises(ValueError, match="Cannot cancel payroll in"):
            payroll.cancel()


class TestDomainEvents:
    def test_creation_event(self):
        """Test that creating a payroll generates a creation event"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        payroll = Payroll.create(employee_id=employee_id, period=period)

        events = payroll.get_domain_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "PayrollCreatedEvent"

    def test_clear_domain_events(self):
        """Test clearing domain events"""
        employee_id = uuid4()
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        payroll = Payroll.create(employee_id=employee_id, period=period)

        assert len(payroll.get_domain_events()) == 1

        payroll.clear_domain_events()

        assert len(payroll.get_domain_events()) == 0


class TestPayrollLineValueObject:
    def test_calculate_amount(self):
        """Test calculating line amount"""
        line = PayrollLine(
            line_type=PayrollLineType.HOURLY_WAGE,
            description="Hourly Wage",
            quantity=Decimal("160"),
            rate=Money(Decimal("25.00"), "USD"),
            amount=Money(Decimal("4000.00"), "USD"),
        )

        calculated_amount = line.calculate_amount()

        assert calculated_amount == Money(Decimal("4000.00"), "USD")

    def test_payroll_line_with_different_currency(self):
        """Test creating payroll line with different currency"""
        line = PayrollLine(
            line_type=PayrollLineType.BASE_SALARY,
            description="Base Salary",
            quantity=Decimal("1"),
            rate=Money(Decimal("5000.00"), "EUR"),
            amount=Money(Decimal("5000.00"), "EUR"),
        )

        assert line.rate.currency == "EUR"
        assert line.amount.currency == "EUR"


class TestPayrollPeriodValueObject:
    def test_create_monthly_period(self):
        """Test creating a monthly payroll period"""
        period = PayrollPeriod(
            period_type=PayrollPeriodType.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        assert period.period_type == PayrollPeriodType.MONTHLY
        assert period.start_date == date(2024, 1, 1)
        assert period.end_date == date(2024, 1, 31)

    def test_create_weekly_period(self):
        """Test creating a weekly payroll period"""
        period = PayrollPeriod(
            period_type=PayrollPeriodType.WEEKLY,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
        )

        assert period.period_type == PayrollPeriodType.WEEKLY
