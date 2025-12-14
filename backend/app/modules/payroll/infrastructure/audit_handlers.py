"""Event handlers for payroll module to emit audit events"""

import logging
from datetime import datetime
from typing import Any

from app.modules.audit.domain.events import AuditLogCreatedEvent
from app.shared.domain.events import get_event_dispatcher
from app.shared.infrastructure.event_registry import EventHandlerRegistry

logger = logging.getLogger(__name__)


class PayrollAuditEventHandler:
    """Handler that listens to payroll events and emits audit events"""

    async def handle_payroll_created(self, event_data: dict[str, Any]) -> None:
        """Handle PayrollCreatedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="PAYROLL",
                entity_id=event_data["payroll_id"],
                action="CREATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "period_start": event_data["period_start"],
                    "period_end": event_data["period_end"],
                },
                changed_by=None,
                metadata={"source_event": "PayrollCreatedEvent"},
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for payroll created: {event_data['payroll_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for payroll created: {e}")

    async def handle_payroll_calculated(self, event_data: dict[str, Any]) -> None:
        """Handle PayrollCalculatedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="PAYROLL",
                entity_id=event_data["payroll_id"],
                action="CALCULATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "gross_pay": str(event_data["gross_pay"]),
                    "net_pay": str(event_data["net_pay"]),
                },
                changed_by=None,
                metadata={"source_event": "PayrollCalculatedEvent"},
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for payroll calculated: {event_data['payroll_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for payroll calculated: {e}")

    async def handle_payroll_approved(self, event_data: dict[str, Any]) -> None:
        """Handle PayrollApprovedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="PAYROLL",
                entity_id=event_data["payroll_id"],
                action="APPROVED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "approved_at": event_data["approved_at"],
                },
                changed_by=event_data.get("approved_by"),
                metadata={"source_event": "PayrollApprovedEvent"},
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for payroll approved: {event_data['payroll_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for payroll approved: {e}")

    async def handle_payroll_processed(self, event_data: dict[str, Any]) -> None:
        """Handle PayrollProcessedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="PAYROLL",
                entity_id=event_data["payroll_id"],
                action="PROCESSED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "net_pay": str(event_data["net_pay"]),
                    "processed_at": event_data["processed_at"],
                },
                changed_by=None,
                metadata={"source_event": "PayrollProcessedEvent"},
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for payroll processed: {event_data['payroll_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for payroll processed: {e}")

    async def handle_payroll_paid(self, event_data: dict[str, Any]) -> None:
        """Handle PayrollPaidEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="PAYROLL",
                entity_id=event_data["payroll_id"],
                action="PAID",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "amount_paid": str(event_data["amount_paid"]),
                    "payment_reference": event_data["payment_reference"],
                    "paid_at": event_data["paid_at"],
                },
                changed_by=None,
                metadata={"source_event": "PayrollPaidEvent"},
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for payroll paid: {event_data['payroll_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for payroll paid: {e}")

    async def handle_payroll_status_changed(self, event_data: dict[str, Any]) -> None:
        """Handle PayrollStatusChangedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="PAYROLL",
                entity_id=event_data["payroll_id"],
                action="STATUS_CHANGED",
                employee_id=None,  # Status change events don't include employee_id
                old_values={"status": event_data["old_status"]},
                new_values={"status": event_data["new_status"]},
                changed_by=None,
                metadata={"source_event": "PayrollStatusChangedEvent"},
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(
                f"Emitted audit event for payroll status changed: {event_data['payroll_id']}"
            )
        except Exception as e:
            logger.error(f"Failed to emit audit event for payroll status changed: {e}")


def register_payroll_audit_handlers(registry: EventHandlerRegistry) -> None:
    """Register payroll audit event handlers"""
    handler = PayrollAuditEventHandler()

    # Register handlers for each payroll event
    registry.register("payroll.payroll-created-event", handler.handle_payroll_created)
    registry.register("payroll.payroll-calculated-event", handler.handle_payroll_calculated)
    registry.register("payroll.payroll-approved-event", handler.handle_payroll_approved)
    registry.register("payroll.payroll-processed-event", handler.handle_payroll_processed)
    registry.register("payroll.payroll-paid-event", handler.handle_payroll_paid)
    registry.register("payroll.payroll-status-changed-event", handler.handle_payroll_status_changed)

    logger.info("Registered payroll audit event handlers")
