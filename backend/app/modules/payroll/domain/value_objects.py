from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.shared.domain.value_objects import Money


class PayrollStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    PROCESSED = "PROCESSED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class PayrollPeriodType(str, Enum):
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"


class PayrollLineType(str, Enum):
    BASE_SALARY = "BASE_SALARY"
    HOURLY_WAGE = "HOURLY_WAGE"
    OVERTIME = "OVERTIME"
    BONUS = "BONUS"
    COMMISSION = "COMMISSION"
    DEDUCTION = "DEDUCTION"
    TAX = "TAX"
    ABSENCE_DEDUCTION = "ABSENCE_DEDUCTION"


class PayrollPeriod(BaseModel):
    """Value object representing a payroll period"""

    period_type: PayrollPeriodType
    start_date: date
    end_date: date

    def contains_date(self, check_date: date) -> bool:
        """Check if a date falls within this period"""
        return self.start_date <= check_date <= self.end_date

    def __str__(self) -> str:
        return f"{self.period_type.value}: {self.start_date} to {self.end_date}"


class PayrollLine(BaseModel):
    """Value object representing a single line item in payroll"""

    line_type: PayrollLineType
    description: str
    quantity: Decimal  # hours, days, or units
    rate: Money
    amount: Money
    reference_id: Optional[UUID] = None  # Reference to source (contract, bonus, etc.)

    def calculate_amount(self) -> Money:
        """Calculate the line amount"""
        return self.rate * self.quantity


class PayrollSummary(BaseModel):
    """Value object for payroll calculation summary"""

    gross_pay: Money
    total_deductions: Money
    total_taxes: Money
    net_pay: Money

    def __str__(self) -> str:
        return f"Gross: {self.gross_pay}, Deductions: {self.total_deductions}, Taxes: {self.total_taxes}, Net: {self.net_pay}"


class PayrollDataCollection(BaseModel):
    """Value object containing all data needed for payroll calculation"""

    employee: Any  # EmployeeDetailView from employee module
    contract_data: Dict[str, Any]  # Contract data dictionary
    bonuses: List[Any]  # List of BonusView from compensation module
    absences: List[Any]  # List of AbsenceView from absence module


class AbsenceImpact(BaseModel):
    """Value object for absence impact on payroll"""

    deduction_amount: Money
    absence_days: int
