from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.modules.payroll.domain.value_objects import (
    PayrollLineType,
    PayrollPeriodType,
    PayrollStatus,
)


class PayrollLineView(BaseModel):
    """View for payroll line items"""

    line_type: PayrollLineType
    description: str
    quantity: Decimal
    rate: Decimal  # We'll serialize Money.amount here
    amount: Decimal  # We'll serialize Money.amount here
    currency: str
    reference_id: Optional[UUID]


class PayrollListView(BaseModel):
    """View for payroll list"""

    id: UUID
    employee_id: UUID
    period_type: PayrollPeriodType
    period_start_date: date
    period_end_date: date
    status: PayrollStatus
    gross_pay: Decimal
    net_pay: Decimal
    currency: str
    created_at: Optional[date]


class PayrollDetailView(BaseModel):
    """View for payroll detail"""

    id: UUID
    employee_id: UUID
    period_type: PayrollPeriodType
    period_start_date: date
    period_end_date: date
    status: PayrollStatus
    gross_pay: Decimal
    total_deductions: Decimal
    total_taxes: Decimal
    net_pay: Decimal
    currency: str
    lines: List[PayrollLineView]
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    processed_at: Optional[datetime]
    paid_at: Optional[datetime]
    payment_reference: Optional[str]
    notes: Optional[str]
    version: str
    created_at: Optional[date]
    updated_at: Optional[date]


class PayrollListResponse(BaseModel):
    """Wrapper for list of payrolls"""

    items: List[PayrollListView]
    total: int
