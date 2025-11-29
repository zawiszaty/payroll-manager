from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from app.modules.payroll.domain.events import (
    PayrollApprovedEvent,
    PayrollCalculatedEvent,
    PayrollCreatedEvent,
    PayrollPaidEvent,
    PayrollProcessedEvent,
    PayrollStatusChangedEvent,
)
from app.modules.payroll.domain.value_objects import (
    PayrollLine,
    PayrollPeriod,
    PayrollStatus,
    PayrollSummary,
)
from app.shared.domain.value_objects import Money


class Payroll:
    """
    Payroll aggregate root
    Represents a single payroll calculation for an employee for a specific period
    """

    def __init__(
        self,
        payroll_id: UUID,
        employee_id: UUID,
        period: PayrollPeriod,
        status: PayrollStatus = PayrollStatus.DRAFT,
        lines: Optional[List[PayrollLine]] = None,
        summary: Optional[PayrollSummary] = None,
        approved_by: Optional[UUID] = None,
        approved_at: Optional[datetime] = None,
        processed_at: Optional[datetime] = None,
        paid_at: Optional[datetime] = None,
        payment_reference: Optional[str] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = payroll_id
        self.employee_id = employee_id
        self.period = period
        self.status = status
        self.lines = lines or []
        self.summary = summary
        self.approved_by = approved_by
        self.approved_at = approved_at
        self.processed_at = processed_at
        self.paid_at = paid_at
        self.payment_reference = payment_reference
        self.notes = notes
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self._domain_events: List = []

    @staticmethod
    def create(employee_id: UUID, period: PayrollPeriod, notes: Optional[str] = None) -> "Payroll":
        """Factory method to create a new payroll"""
        payroll_id = uuid4()
        payroll = Payroll(
            payroll_id=payroll_id,
            employee_id=employee_id,
            period=period,
            status=PayrollStatus.DRAFT,
            notes=notes,
        )

        payroll._add_domain_event(
            PayrollCreatedEvent(
                payroll_id=payroll_id,
                employee_id=employee_id,
                period_start=period.start_date,
                period_end=period.end_date,
            )
        )

        return payroll

    def add_line(self, line: PayrollLine) -> None:
        """Add a line item to the payroll"""
        if self.status not in [PayrollStatus.DRAFT, PayrollStatus.PENDING_APPROVAL]:
            raise ValueError(f"Cannot add lines to payroll in {self.status} status")

        self.lines.append(line)
        self.updated_at = datetime.utcnow()

    def calculate(self) -> None:
        """Calculate payroll totals using Money value objects"""
        if not self.lines:
            raise ValueError("Cannot calculate payroll without line items")

        # Get currency from first line
        currency = self.lines[0].amount.currency if self.lines else "USD"

        # Calculate gross pay (income lines)
        gross_lines = [
            line.amount
            for line in self.lines
            if line.line_type.value
            in [
                "BASE_SALARY",
                "HOURLY_WAGE",
                "OVERTIME",
                "BONUS",
                "COMMISSION",
            ]
        ]
        gross_pay: Money = gross_lines[0] if gross_lines else Money(Decimal("0"), currency)
        for amount in gross_lines[1:]:
            gross_pay = gross_pay + amount

        # Calculate total deductions
        deduction_lines = [
            line.amount
            for line in self.lines
            if line.line_type.value in ["DEDUCTION", "ABSENCE_DEDUCTION"]
        ]
        total_deductions: Money = deduction_lines[0] if deduction_lines else Money(Decimal("0"), currency)
        for amount in deduction_lines[1:]:
            total_deductions = total_deductions + amount

        # Calculate total taxes
        tax_lines = [
            line.amount for line in self.lines if line.line_type.value == "TAX"
        ]
        total_taxes: Money = tax_lines[0] if tax_lines else Money(Decimal("0"), currency)
        for amount in tax_lines[1:]:
            total_taxes = total_taxes + amount

        # Calculate net pay
        net_pay: Money = gross_pay - total_deductions - total_taxes

        self.summary = PayrollSummary(
            gross_pay=gross_pay,
            total_deductions=total_deductions,
            total_taxes=total_taxes,
            net_pay=net_pay,
        )

        self.updated_at = datetime.utcnow()

        self._add_domain_event(
            PayrollCalculatedEvent(
                payroll_id=self.id,
                employee_id=self.employee_id,
                gross_pay=gross_pay.amount,
                net_pay=net_pay.amount,
            )
        )

    def submit_for_approval(self) -> None:
        """Submit payroll for approval"""
        if self.status != PayrollStatus.DRAFT:
            raise ValueError(f"Cannot submit payroll in {self.status} status")

        if not self.summary:
            raise ValueError("Payroll must be calculated before submission")

        old_status = self.status
        self.status = PayrollStatus.PENDING_APPROVAL
        self.updated_at = datetime.utcnow()

        self._add_domain_event(
            PayrollStatusChangedEvent(
                payroll_id=self.id, old_status=old_status, new_status=self.status
            )
        )

    def approve(self, approved_by: UUID) -> None:
        """Approve the payroll"""
        if self.status != PayrollStatus.PENDING_APPROVAL:
            raise ValueError(f"Cannot approve payroll in {self.status} status")

        old_status = self.status
        self.status = PayrollStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        self._add_domain_event(
            PayrollApprovedEvent(
                payroll_id=self.id,
                employee_id=self.employee_id,
                approved_by=approved_by,
                approved_at=self.approved_at,
            )
        )

        self._add_domain_event(
            PayrollStatusChangedEvent(
                payroll_id=self.id, old_status=old_status, new_status=self.status
            )
        )

    def process(self) -> None:
        """Process the payroll for payment"""
        if self.status != PayrollStatus.APPROVED:
            raise ValueError(f"Cannot process payroll in {self.status} status")

        old_status = self.status
        self.status = PayrollStatus.PROCESSED
        self.processed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        self._add_domain_event(
            PayrollProcessedEvent(
                payroll_id=self.id,
                employee_id=self.employee_id,
                net_pay=self.summary.net_pay.amount,
                processed_at=self.processed_at,
            )
        )

        self._add_domain_event(
            PayrollStatusChangedEvent(
                payroll_id=self.id, old_status=old_status, new_status=self.status
            )
        )

    def mark_as_paid(self, payment_reference: str) -> None:
        """Mark the payroll as paid"""
        if self.status != PayrollStatus.PROCESSED:
            raise ValueError(f"Cannot mark payroll as paid in {self.status} status")

        old_status = self.status
        self.status = PayrollStatus.PAID
        self.payment_reference = payment_reference
        self.paid_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        self._add_domain_event(
            PayrollPaidEvent(
                payroll_id=self.id,
                employee_id=self.employee_id,
                amount_paid=self.summary.net_pay.amount,
                payment_reference=payment_reference,
                paid_at=self.paid_at,
            )
        )

        self._add_domain_event(
            PayrollStatusChangedEvent(
                payroll_id=self.id, old_status=old_status, new_status=self.status
            )
        )

    def cancel(self) -> None:
        """Cancel the payroll"""
        if self.status in [PayrollStatus.PROCESSED, PayrollStatus.PAID]:
            raise ValueError(f"Cannot cancel payroll in {self.status} status")

        old_status = self.status
        self.status = PayrollStatus.CANCELLED
        self.updated_at = datetime.utcnow()

        self._add_domain_event(
            PayrollStatusChangedEvent(
                payroll_id=self.id, old_status=old_status, new_status=self.status
            )
        )

    def _add_domain_event(self, event) -> None:
        """Add a domain event to the aggregate"""
        self._domain_events.append(event)

    def get_domain_events(self) -> List:
        """Get all domain events"""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear all domain events"""
        self._domain_events.clear()
