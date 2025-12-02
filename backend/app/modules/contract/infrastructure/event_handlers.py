"""Event handlers for contract module to emit audit events"""

import logging
from datetime import datetime
from typing import Any

from app.modules.audit.domain.events import AuditLogCreatedEvent
from app.shared.domain.events import get_event_dispatcher
from app.shared.infrastructure.event_registry import EventHandlerRegistry

logger = logging.getLogger(__name__)


class ContractAuditEventHandler:
    """Handler that listens to contract events and emits audit events"""

    async def handle_contract_created(self, event_data: dict[str, Any]) -> None:
        """Handle ContractCreatedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="CONTRACT",
                entity_id=event_data["contract_id"],
                action="CREATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "contract_type": event_data["contract_type"],
                    "rate_amount": str(event_data["rate_amount"]),
                    "rate_currency": event_data["rate_currency"],
                    "valid_from": event_data["valid_from"],
                    "valid_to": event_data.get("valid_to"),
                },
                changed_by=event_data.get("changed_by"),
                metadata={"source_event": "ContractCreatedEvent"},
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for contract created: {event_data['contract_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for contract created: {e}")

    async def handle_contract_activated(self, event_data: dict[str, Any]) -> None:
        """Handle ContractActivatedEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="CONTRACT",
                entity_id=event_data["contract_id"],
                action="ACTIVATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values=None,
                changed_by=event_data.get("changed_by"),
                metadata={
                    "source_event": "ContractActivatedEvent",
                    "contract_type": event_data["contract_type"],
                    "activated_at": event_data["activated_at"],
                },
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for contract activated: {event_data['contract_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for contract activated: {e}")

    async def handle_contract_canceled(self, event_data: dict[str, Any]) -> None:
        """Handle ContractCanceledEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="CONTRACT",
                entity_id=event_data["contract_id"],
                action="CANCELED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values=None,
                changed_by=event_data.get("changed_by"),
                metadata={
                    "source_event": "ContractCanceledEvent",
                    "contract_type": event_data["contract_type"],
                    "cancellation_reason": event_data["cancellation_reason"],
                    "canceled_at": event_data["canceled_at"],
                },
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for contract canceled: {event_data['contract_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for contract canceled: {e}")

    async def handle_contract_expired(self, event_data: dict[str, Any]) -> None:
        """Handle ContractExpiredEvent and emit AuditLogCreatedEvent"""
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="CONTRACT",
                entity_id=event_data["contract_id"],
                action="EXPIRED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values=None,
                changed_by=event_data.get("changed_by"),
                metadata={
                    "source_event": "ContractExpiredEvent",
                    "contract_type": event_data["contract_type"],
                    "expired_at": event_data["expired_at"],
                },
                occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
            )

            dispatcher = get_event_dispatcher()
            await dispatcher.dispatch(audit_event)

            logger.info(f"Emitted audit event for contract expired: {event_data['contract_id']}")
        except Exception as e:
            logger.error(f"Failed to emit audit event for contract expired: {e}")


def register_contract_audit_handlers(registry: EventHandlerRegistry) -> None:
    """Register contract event handlers that emit audit events"""
    handler = ContractAuditEventHandler()

    # Listen to contract events and emit audit events
    registry.register("contract.contract-created-event", handler.handle_contract_created)
    registry.register("contract.contract-activated-event", handler.handle_contract_activated)
    registry.register("contract.contract-canceled-event", handler.handle_contract_canceled)
    registry.register("contract.contract-expired-event", handler.handle_contract_expired)

    logger.info("Registered contract audit event handlers")
