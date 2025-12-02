from uuid import UUID

from app.shared.domain.events import DomainEvent


class ReportGenerationRequestedEvent(DomainEvent):
    """Event emitted when a report generation is requested"""

    report_id: UUID
    report_type: str
    report_format: str
    parameters: dict


class ReportGenerationStartedEvent(DomainEvent):
    """Event emitted when report generation starts"""

    report_id: UUID
    report_type: str


class ReportGenerationCompletedEvent(DomainEvent):
    """Event emitted when report generation completes successfully"""

    report_id: UUID
    report_type: str
    file_path: str


class ReportGenerationFailedEvent(DomainEvent):
    """Event emitted when report generation fails"""

    report_id: UUID
    report_type: str
    error_message: str
