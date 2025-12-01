from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.modules.audit.domain.value_objects import AuditAction, EntityType


class AuditLogORM(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type: Mapped[EntityType] = mapped_column(Enum(EntityType), nullable=False, index=True)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    employee_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), nullable=True, index=True
    )
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False, index=True)
    old_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    changed_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    event_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    __table_args__ = (
        Index("idx_audit_entity_type_id", "entity_type", "entity_id"),
        Index("idx_audit_employee_occurred", "employee_id", "occurred_at"),
        Index("idx_audit_occurred_at", "occurred_at"),
    )
