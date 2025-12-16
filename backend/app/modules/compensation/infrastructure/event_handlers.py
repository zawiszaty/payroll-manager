import logging
from datetime import datetime
from typing import Any

from app.modules.audit.domain.events import AuditLogCreatedEvent
from app.modules.compensation.application.commands import CreateRateCommand
from app.modules.compensation.application.handlers import CreateRateHandler
from app.modules.compensation.domain.value_objects import RateType
from app.modules.compensation.infrastructure.repository import SQLAlchemyRateRepository
from app.shared.domain.events import get_event_dispatcher
from app.shared.infrastructure.event_registry import EventHandlerRegistry

logger = logging.getLogger(__name__)


class CompensationEventHandler:
    async def handle_rate_created(self, event_data: dict[str, Any]) -> None:
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="RATE",
                entity_id=event_data["rate_id"],
                action="CREATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "rate_type": event_data["rate_type"],
                    "amount": str(event_data["amount"]),
                    "currency": event_data["currency"],
                    "valid_from": event_data["valid_from"].isoformat(),
                    "valid_to": event_data["valid_to"].isoformat()
                    if event_data.get("valid_to")
                    else None,
                },
                changed_by=None,
                occurred_at=datetime.utcnow(),
                metadata={
                    "event_type": "RateCreatedEvent",
                    "rate_type": event_data["rate_type"],
                },
            )
            await get_event_dispatcher().dispatch(audit_event)
            logger.info(f"Published audit event for rate creation: {event_data['rate_id']}")
        except Exception as e:
            logger.error(f"Error handling rate created event: {e}")

    async def handle_bonus_created(self, event_data: dict[str, Any]) -> None:
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="BONUS",
                entity_id=event_data["bonus_id"],
                action="CREATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "bonus_type": event_data["bonus_type"],
                    "amount": str(event_data["amount"]),
                    "currency": event_data["currency"],
                    "payment_date": event_data["payment_date"].isoformat(),
                },
                changed_by=None,
                occurred_at=datetime.utcnow(),
                metadata={
                    "event_type": "BonusCreatedEvent",
                    "bonus_type": event_data["bonus_type"],
                },
            )
            await get_event_dispatcher().dispatch(audit_event)
            logger.info(f"Published audit event for bonus creation: {event_data['bonus_id']}")
        except Exception as e:
            logger.error(f"Error handling bonus created event: {e}")

    async def handle_deduction_created(self, event_data: dict[str, Any]) -> None:
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="DEDUCTION",
                entity_id=event_data["deduction_id"],
                action="CREATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "deduction_type": event_data["deduction_type"],
                    "amount": str(event_data["amount"]),
                    "currency": event_data["currency"],
                    "valid_from": event_data["valid_from"].isoformat(),
                    "valid_to": event_data["valid_to"].isoformat()
                    if event_data.get("valid_to")
                    else None,
                },
                changed_by=None,
                occurred_at=datetime.utcnow(),
                metadata={
                    "event_type": "DeductionCreatedEvent",
                    "deduction_type": event_data["deduction_type"],
                },
            )
            await get_event_dispatcher().dispatch(audit_event)
            logger.info(
                f"Published audit event for deduction creation: {event_data['deduction_id']}"
            )
        except Exception as e:
            logger.error(f"Error handling deduction created event: {e}")

    async def handle_overtime_created(self, event_data: dict[str, Any]) -> None:
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="OVERTIME",
                entity_id=event_data["overtime_id"],
                action="CREATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "multiplier": str(event_data["multiplier"]),
                    "threshold_hours": event_data["threshold_hours"],
                    "valid_from": event_data["valid_from"].isoformat(),
                    "valid_to": event_data["valid_to"].isoformat()
                    if event_data.get("valid_to")
                    else None,
                },
                changed_by=None,
                occurred_at=datetime.utcnow(),
                metadata={
                    "event_type": "OvertimeCreatedEvent",
                },
            )
            await get_event_dispatcher().dispatch(audit_event)
            logger.info(f"Published audit event for overtime creation: {event_data['overtime_id']}")
        except Exception as e:
            logger.error(f"Error handling overtime created event: {e}")

    async def handle_sick_leave_created(self, event_data: dict[str, Any]) -> None:
        try:
            audit_event = AuditLogCreatedEvent(
                entity_type="SICK_LEAVE",
                entity_id=event_data["sick_leave_id"],
                action="CREATED",
                employee_id=event_data["employee_id"],
                old_values=None,
                new_values={
                    "percentage": str(event_data["percentage"]),
                    "max_days": event_data.get("max_days"),
                    "valid_from": event_data["valid_from"].isoformat(),
                    "valid_to": event_data["valid_to"].isoformat()
                    if event_data.get("valid_to")
                    else None,
                },
                changed_by=None,
                occurred_at=datetime.utcnow(),
                metadata={
                    "event_type": "SickLeaveCreatedEvent",
                },
            )
            await get_event_dispatcher().dispatch(audit_event)
            logger.info(
                f"Published audit event for sick leave creation: {event_data['sick_leave_id']}"
            )
        except Exception as e:
            logger.error(f"Error handling sick leave created event: {e}")

    async def handle_contract_created(self, event_data: dict[str, Any]) -> None:
        """Handle ContractCreatedEvent: emit audit event AND automatically create a Rate"""
        from datetime import date, datetime

        # First, emit audit event for the contract creation
        try:
            # Handle date fields - convert to date objects if they're strings
            valid_from = event_data["valid_from"]
            if isinstance(valid_from, str):
                valid_from = date.fromisoformat(valid_from)

            valid_to = event_data.get("valid_to")
            if valid_to and isinstance(valid_to, str):
                valid_to = date.fromisoformat(valid_to)

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
                    "valid_from": valid_from.isoformat()
                    if hasattr(valid_from, "isoformat")
                    else str(valid_from),
                    "valid_to": valid_to.isoformat()
                    if valid_to and hasattr(valid_to, "isoformat")
                    else (str(valid_to) if valid_to else None),
                },
                changed_by=None,  # System-generated
                occurred_at=datetime.now(),
                metadata={
                    "event_type": "ContractCreatedEvent",
                    "contract_type": event_data["contract_type"],
                },
            )
            await get_event_dispatcher().dispatch(audit_event)
            logger.info(f"Published audit event for contract creation: {event_data['contract_id']}")
        except Exception as e:
            logger.error(f"Error emitting audit event for contract: {e}")

        # Then, automatically create a Rate from the contract
        try:
            from app.database import get_db

            logger.info(f"Creating automatic rate from contract: {event_data['contract_id']}")

            # Map contract type to rate type
            contract_type = event_data["contract_type"]
            rate_type_mapping = {
                "fixed_monthly": RateType.BASE_SALARY,
                "hourly": RateType.HOURLY_RATE,
                "b2b_daily": RateType.DAILY_RATE,
                "b2b_hourly": RateType.HOURLY_RATE,
                "task_based": RateType.BASE_SALARY,  # Fallback to BASE_SALARY since there's no PIECE_RATE
                "commission_based": RateType.BASE_SALARY,  # Fallback to BASE_SALARY since there's no COMMISSION
            }

            rate_type = rate_type_mapping.get(contract_type, RateType.BASE_SALARY)

            # Handle date fields for rate command
            rate_valid_from = event_data["valid_from"]
            if isinstance(rate_valid_from, str):
                rate_valid_from = date.fromisoformat(rate_valid_from)

            rate_valid_to = event_data.get("valid_to")
            if rate_valid_to and isinstance(rate_valid_to, str):
                rate_valid_to = date.fromisoformat(rate_valid_to)

            # Handle amount - ensure it's a Decimal
            from decimal import Decimal

            rate_amount = event_data["rate_amount"]
            if isinstance(rate_amount, str):
                rate_amount = Decimal(rate_amount)
            elif not isinstance(rate_amount, Decimal):
                rate_amount = Decimal(str(rate_amount))

            # Create rate command
            command = CreateRateCommand(
                employee_id=event_data["employee_id"],
                rate_type=rate_type,
                amount=rate_amount,
                currency=event_data["rate_currency"],
                valid_from=rate_valid_from,
                valid_to=rate_valid_to,
                description=f"Auto-created from contract {event_data['contract_id']}",
            )

            # Get database session and create rate
            async for session in get_db():
                try:
                    repository = SQLAlchemyRateRepository(session)
                    handler = CreateRateHandler(repository)
                    rate = await handler.handle(command)
                    await session.commit()
                    logger.info(
                        f"Successfully created rate {rate.id} from contract {event_data['contract_id']}"
                    )
                    break
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Failed to create rate from contract: {e}")
                    raise

        except Exception as e:
            logger.error(
                f"Error handling contract created event for compensation: {e}", exc_info=True
            )


def register_compensation_handlers(registry: EventHandlerRegistry) -> None:
    handler = CompensationEventHandler()

    # Register compensation event handlers (for audit logging)
    registry.register("compensation.rate-created-event", handler.handle_rate_created)
    registry.register("compensation.bonus-created-event", handler.handle_bonus_created)
    registry.register("compensation.deduction-created-event", handler.handle_deduction_created)
    registry.register("compensation.overtime-created-event", handler.handle_overtime_created)
    registry.register("compensation.sick-leave-created-event", handler.handle_sick_leave_created)

    # Register contract event handler (for automatic rate creation)
    registry.register("contract.contract-created-event", handler.handle_contract_created)

    logger.info("Registered compensation event handlers")
