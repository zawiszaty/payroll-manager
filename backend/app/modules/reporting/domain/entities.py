from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.modules.reporting.domain.value_objects import (
    ReportFormat,
    ReportParameters,
    ReportStatus,
    ReportType,
)


@dataclass
class Report:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    report_type: ReportType = ReportType.CUSTOM
    format: ReportFormat = ReportFormat.PDF
    status: ReportStatus = ReportStatus.PENDING
    parameters: ReportParameters = field(default_factory=lambda: ReportParameters())
    file_path: str | None = None
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    _domain_events: list = field(default_factory=list, init=False, repr=False)

    def start_processing(self) -> None:
        if self.status != ReportStatus.PENDING:
            raise ValueError(f"Cannot start processing report in {self.status.value} status")
        self.status = ReportStatus.PROCESSING

    def complete(self, file_path: str) -> None:
        if self.status != ReportStatus.PROCESSING:
            raise ValueError(f"Cannot complete report in {self.status.value} status")
        self.status = ReportStatus.COMPLETED
        self.file_path = file_path
        self.completed_at = datetime.now()

    def fail(self, error_message: str) -> None:
        if self.status not in [ReportStatus.PENDING, ReportStatus.PROCESSING]:
            raise ValueError(f"Cannot fail report in {self.status.value} status")
        self.status = ReportStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()

    def is_completed(self) -> bool:
        return self.status == ReportStatus.COMPLETED

    def is_failed(self) -> bool:
        return self.status == ReportStatus.FAILED

    def is_processing(self) -> bool:
        return self.status == ReportStatus.PROCESSING

    def is_pending(self) -> bool:
        return self.status == ReportStatus.PENDING

    def _add_domain_event(self, event) -> None:
        """Add a domain event to the entity"""
        self._domain_events.append(event)

    def get_domain_events(self) -> list:
        """Get all domain events"""
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Clear all domain events"""
        self._domain_events.clear()
