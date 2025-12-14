from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID

from app.modules.payroll.domain.value_objects import PayrollPeriodType, PayrollStatus


@dataclass
class CreatePayrollCommand:
    employee_id: UUID
    period_type: PayrollPeriodType
    period_start_date: date
    period_end_date: date
    notes: Optional[str] = None


@dataclass
class CalculatePayrollCommand:
    payroll_id: UUID
    working_days: Optional[int] = None


@dataclass
class ApprovePayrollCommand:
    payroll_id: UUID
    approved_by: UUID


@dataclass
class ProcessPayrollCommand:
    payroll_id: UUID


@dataclass
class MarkPayrollAsPaidCommand:
    payroll_id: UUID
    payment_reference: str


@dataclass
class UpdatePayrollStatusCommand:
    payroll_id: UUID
    new_status: PayrollStatus
