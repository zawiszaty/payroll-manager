from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateReportRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    report_type: str = Field(
        ...,
        pattern="^(payroll_summary|employee_compensation|absence_summary|timesheet_summary|tax_report|custom)$",
    )
    format: str = Field(..., pattern="^(pdf|csv|xlsx|json)$")
    employee_id: str | None = None
    department: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    additional_filters: dict[str, str] | None = None


class ReportResponse(BaseModel):
    id: UUID
    name: str
    report_type: str
    format: str
    status: str
    parameters: dict[str, str | None]
    file_path: str | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    @classmethod
    def from_entity(cls, report):
        return cls(
            id=report.id,
            name=report.name,
            report_type=report.report_type.value,
            format=report.format.value,
            status=report.status.value,
            parameters={
                "employee_id": report.parameters.employee_id,
                "department": report.parameters.department,
                "start_date": report.parameters.start_date,
                "end_date": report.parameters.end_date,
                "additional_filters": report.parameters.additional_filters,
            },
            file_path=report.file_path,
            error_message=report.error_message,
            created_at=report.created_at,
            completed_at=report.completed_at,
        )


class ReportListResponse(BaseModel):
    reports: list[ReportResponse]
