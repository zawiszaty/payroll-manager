from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateReportCommand:
    name: str
    report_type: str
    format: str
    employee_id: str | None = None
    department: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    additional_filters: dict[str, str] | None = None


@dataclass
class GenerateReportCommand:
    report_id: UUID


@dataclass
class DeleteReportCommand:
    report_id: UUID
