"""Event handlers for audit module"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database import AsyncSessionLocal
from app.modules.audit.domain.models import AuditLog
from app.modules.audit.domain.value_objects import AuditAction, EntityType
from app.modules.audit.infrastructure.repository import SQLAlchemyAuditLogRepository
from app.shared.infrastructure.event_registry import EventHandlerRegistry

logger = logging.getLogger(__name__)


class AuditEventHandler:
    """Handler for audit-related events"""

    def __init__(self, session_factory: async_sessionmaker = AsyncSessionLocal):
        self.session_factory = session_factory

    async def handle_audit_log_created(self, event_data: dict[str, Any]) -> None:
        """Handle AuditLogCreatedEvent - create audit log from audit event"""
        async with self.session_factory() as session:
            try:
                repository = SQLAlchemyAuditLogRepository(session)

                # Parse entity type and action from event data
                entity_type = EntityType[event_data["entity_type"]]
                action = AuditAction[event_data["action"]]

                # Parse occurred_at - it might already be a datetime or a string
                occurred_at = event_data.get("occurred_at")
                if isinstance(occurred_at, str):
                    occurred_at = datetime.fromisoformat(occurred_at)
                elif not isinstance(occurred_at, datetime):
                    occurred_at = None

                audit_log = AuditLog.create(
                    entity_type=entity_type,
                    entity_id=event_data["entity_id"],
                    action=action,
                    employee_id=event_data.get("employee_id"),
                    old_values=event_data.get("old_values"),
                    new_values=event_data.get("new_values"),
                    changed_by=event_data.get("changed_by"),
                    metadata=event_data.get("metadata"),
                    occurred_at=occurred_at,
                )
                await repository.save(audit_log)
                await session.commit()
                logger.info(f"Created audit log for {entity_type.value} {action.value}")
            except Exception as e:
                logger.error(f"Failed to create audit log: {e}", exc_info=True)
                await session.rollback()


def register_audit_handlers(registry: EventHandlerRegistry) -> None:
    """Register all audit event handlers"""
    handler = AuditEventHandler()

    # Register only the audit-specific event
    registry.register("audit.audit-log-created-event", handler.handle_audit_log_created)

    logger.info("Registered audit event handlers")
