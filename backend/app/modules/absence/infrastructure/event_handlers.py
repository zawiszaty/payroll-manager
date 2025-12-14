"""Event handlers for the absence module"""

import logging
from datetime import date, datetime
from typing import Any
from uuid import UUID

from app.database import AsyncSessionLocal
from app.modules.absence.application.commands import CreateAbsenceCommand
from app.modules.absence.application.handlers import CreateAbsenceHandler
from app.modules.absence.domain.repository import (
    AbsenceBalanceRepository,
    AbsenceRepository,
)
from app.modules.absence.domain.value_objects import AbsenceType
from app.modules.absence.infrastructure.repository import (
    SQLAlchemyAbsenceBalanceRepository,
    SQLAlchemyAbsenceRepository,
)
from app.modules.audit.domain.events import AuditLogCreatedEvent
from app.shared.domain.events import get_event_dispatcher
from app.shared.infrastructure.event_registry import EventHandlerRegistry

logger = logging.getLogger(__name__)


class AbsenceEventHandler:
    """Handler for absence-related events"""

    async def handle_absence_requested(self, event_data: dict[str, Any]) -> None:
        """
        Handles AbsenceRequestedEvent from external systems.
        Creates a pending absence request in the system.

        Args:
            event_data: Event payload containing absence details
        """
        try:
            logger.info(f"Processing AbsenceRequestedEvent: {event_data.get('event_id')}")

            # Extract data from event
            data = event_data.get("data", {})
            employee_id = UUID(data["employee_id"])
            absence_type = AbsenceType(data["absence_type"])
            start_date = date.fromisoformat(data["start_date"])
            end_date = date.fromisoformat(data["end_date"])
            reason = data.get("reason")
            notes = data.get("notes")

            # Create command
            command = CreateAbsenceCommand(
                employee_id=employee_id,
                absence_type=absence_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                notes=notes,
            )

            # Use a new session for this operation
            async with AsyncSessionLocal() as session:
                try:
                    # Create repositories
                    absence_repo: AbsenceRepository = SQLAlchemyAbsenceRepository(session)
                    balance_repo: AbsenceBalanceRepository = SQLAlchemyAbsenceBalanceRepository(
                        session
                    )

                    # Handle command
                    handler = CreateAbsenceHandler(absence_repo, balance_repo)
                    absence = await handler.handle(command)

                    await session.commit()

                    logger.info(
                        f"Created absence {absence.id} for employee {employee_id} "
                        f"from external event {event_data.get('event_id')}"
                    )
                except Exception:
                    await session.rollback()
                    raise

        except Exception as e:
            logger.error(f"Error handling AbsenceRequestedEvent: {e}", exc_info=True)
            raise


class AbsenceAuditEventHandler:
    """Handler that listens to absence events and emits audit events"""

    async def handle_absence_created(self, event_data: dict[str, Any]) -> None:
        """Handle AbsenceCreatedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="ABSENCE",
                entity_id=event_data["absence_id"],
                action="CREATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "absence_type": event_data["absence_type"],
                    "start_date": event_data["start_date"],
                    "end_date": event_data["end_date"],
                    "reason": event_data.get("reason"),
                    "status": event_data["status"],
                },
                changed_by=None,
                metadata={"source_event": "AbsenceCreatedEvent"},
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for absence created: {event_data['absence_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for absence created: {e}")

    async def handle_absence_approved(self, event_data: dict[str, Any]) -> None:
        """Handle AbsenceApprovedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="ABSENCE",
                entity_id=event_data["absence_id"],
                action="APPROVED",
                employee_id=event_data["employee_id"],
                old_values={"status": "pending"},
                new_values={"status": "approved"},
                changed_by=event_data.get("approved_by"),
                metadata={
                    "source_event": "AbsenceApprovedEvent",
                    "absence_type": event_data["absence_type"],
                    "start_date": event_data["start_date"],
                    "end_date": event_data["end_date"],
                },
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for absence approved: {event_data['absence_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for absence approved: {e}")

    async def handle_absence_rejected(self, event_data: dict[str, Any]) -> None:
        """Handle AbsenceRejectedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="ABSENCE",
                entity_id=event_data["absence_id"],
                action="REJECTED",
                employee_id=event_data["employee_id"],
                old_values={"status": "pending"},
                new_values={"status": "rejected"},
                changed_by=event_data.get("rejected_by"),
                metadata={
                    "source_event": "AbsenceRejectedEvent",
                    "absence_type": event_data["absence_type"],
                    "start_date": event_data["start_date"],
                    "end_date": event_data["end_date"],
                },
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for absence rejected: {event_data['absence_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for absence rejected: {e}")

    async def handle_absence_cancelled(self, event_data: dict[str, Any]) -> None:
        """Handle AbsenceCancelledEvent and emit AuditLogCreatedEvent"""
        try:
            old_status = "approved" if event_data["was_approved"] else "pending"
            audit_event = AuditLogCreatedEvent(
                entity_type="ABSENCE",
                entity_id=event_data["absence_id"],
                action="CANCELED",  # Use American spelling to match AuditAction enum
                employee_id=event_data["employee_id"],
                old_values={"status": old_status},
                new_values={"status": "cancelled"},
                changed_by=event_data.get("cancelled_by"),
                metadata={
                    "source_event": "AbsenceCancelledEvent",
                    "absence_type": event_data["absence_type"],
                    "start_date": event_data["start_date"],
                    "end_date": event_data["end_date"],
                    "was_approved": event_data["was_approved"],
                },
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for absence cancelled: {event_data['absence_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for absence cancelled: {e}")


def register_absence_handlers(registry: EventHandlerRegistry) -> None:
    """Register absence event handlers"""
    handler = AbsenceEventHandler()

    # Register external event handler (from external systems)
    # The event consumer expects the format: module.event-name
    registry.register("absence.absence-requested-event", handler.handle_absence_requested)

    logger.info("Registered absence event handlers")


def register_absence_audit_handlers(registry: EventHandlerRegistry) -> None:
    """Register absence event handlers that emit audit events"""
    handler = AbsenceAuditEventHandler()

    # Listen to absence events and emit audit events
    registry.register("absence.absence-created-event", handler.handle_absence_created)
    registry.register("absence.absence-approved-event", handler.handle_absence_approved)
    registry.register("absence.absence-rejected-event", handler.handle_absence_rejected)
    registry.register("absence.absence-cancelled-event", handler.handle_absence_cancelled)

    logger.info("Registered absence audit event handlers")
