"""Event handlers for employee module to emit audit events"""

import logging
from datetime import datetime
from typing import Any

from app.modules.audit.domain.events import AuditLogCreatedEvent
from app.shared.domain.events import get_event_dispatcher
from app.shared.infrastructure.event_registry import EventHandlerRegistry

logger = logging.getLogger(__name__)


class EmployeeAuditEventHandler:
    """Handler that listens to employee events and emits audit events"""

    async def handle_employee_created(self, event_data: dict[str, Any]) -> None:
        """Handle EmployeeCreatedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="EMPLOYEE",
                entity_id=event_data["employee_id"],
                action="CREATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "first_name": event_data["first_name"],
                    "last_name": event_data["last_name"],
                    "email": event_data["email"],
                    "hire_date": event_data.get("hire_date"),
                },
                changed_by=event_data.get("changed_by"),
                metadata={"source_event": "EmployeeCreatedEvent"},
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for employee created: {event_data['employee_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for employee created: {e}")

    async def handle_employee_updated(self, event_data: dict[str, Any]) -> None:
        """Handle EmployeeUpdatedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="EMPLOYEE",
                entity_id=event_data["employee_id"],
                action="UPDATED",
                employee_id=event_data["employee_id"],
                old_values=event_data["old_values"],
                new_values=event_data["new_values"],
                changed_by=event_data.get("changed_by"),
                metadata={"source_event": "EmployeeUpdatedEvent"},
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for employee updated: {event_data['employee_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for employee updated: {e}")

    async def handle_employee_status_changed(self, event_data: dict[str, Any]) -> None:
        """Handle EmployeeStatusChangedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="EMPLOYEE",
                entity_id=event_data["employee_id"],
                action="STATUS_CHANGED",
                employee_id=event_data["employee_id"],
                old_values={"status": event_data["old_status"]},
                new_values={"status": event_data["new_status"]},
                changed_by=event_data.get("changed_by"),
                metadata={
                    "source_event": "EmployeeStatusChangedEvent",
                    "valid_from": event_data["status_valid_from"],
                    "valid_to": event_data.get("status_valid_to"),
                    "reason": event_data.get("reason"),
                },
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(
                f"Emitted audit event for employee status changed: {event_data['employee_id']}"
            )
        except Exception as e:
            logger.error(f"Failed to emit audit event for employee status changed: {e}")


def register_employee_audit_handlers(registry: EventHandlerRegistry) -> None:
    """Register employee event handlers that emit audit events"""
    handler = EmployeeAuditEventHandler()

    # Listen to employee events and emit audit events
    registry.register("employee.employee-created-event", handler.handle_employee_created)
    registry.register("employee.employee-updated-event", handler.handle_employee_updated)
    registry.register(
        "employee.employee-status-changed-event", handler.handle_employee_status_changed
    )

    logger.info("Registered employee audit event handlers")
