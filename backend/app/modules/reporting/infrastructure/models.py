from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.database import Base
from app.modules.reporting.domain.value_objects import (
    ReportFormat,
    ReportStatus,
    ReportType,
)


class ReportORM(Base):
    __tablename__ = "reports"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    report_type: ReportType = Column(
        Enum(ReportType, native_enum=False, length=50),
        nullable=False,
        index=True,
    )
    format: ReportFormat = Column(
        Enum(ReportFormat, native_enum=False, length=20),
        nullable=False,
    )
    status: ReportStatus = Column(
        Enum(ReportStatus, native_enum=False, length=20),
        nullable=False,
        index=True,
    )
    parameters = Column(JSON, nullable=True)
    file_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict[str, str | UUID | datetime | dict | None]:
        return {
            "id": self.id,
            "name": self.name,
            "report_type": self.report_type.value if self.report_type else None,
            "format": self.format.value if self.format else None,
            "status": self.status.value if self.status else None,
            "parameters": self.parameters,
            "file_path": self.file_path,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }
