from dataclasses import dataclass
from enum import Enum


class ReportType(Enum):
    PAYROLL_SUMMARY = "payroll_summary"
    EMPLOYEE_COMPENSATION = "employee_compensation"
    ABSENCE_SUMMARY = "absence_summary"
    TIMESHEET_SUMMARY = "timesheet_summary"
    TAX_REPORT = "tax_report"
    CUSTOM = "custom"


class ReportFormat(Enum):
    PDF = "pdf"
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"


class ReportStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ReportParameters:
    employee_id: str | None = None
    department: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    additional_filters: dict[str, str] | None = None

    def __post_init__(self) -> None:
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("Start date must be before or equal to end date")
