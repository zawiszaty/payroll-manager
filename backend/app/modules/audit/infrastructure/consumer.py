import asyncio
import json
import logging
from datetime import datetime

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.modules.audit.domain.models import AuditLog
from app.modules.audit.domain.value_objects import AuditAction, EntityType
from app.modules.audit.infrastructure.repository import SQLAlchemyAuditLogRepository

logger = logging.getLogger(__name__)
settings = get_settings()


class AuditEventConsumer:
    def __init__(self, session_factory: async_sessionmaker = AsyncSessionLocal):
        self.session_factory = session_factory
        self.connection = None
        self.channel = None

    async def connect(self) -> None:
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            exchange = await self.channel.declare_exchange(
                "domain_events", aio_pika.ExchangeType.TOPIC, durable=True
            )

            queue = await self.channel.declare_queue("audit_events", durable=True)

            # Bind to all audit-related events using wildcard
            # Format: event.payroll-manager.employee.* and event.payroll-manager.contract.*
            await queue.bind(exchange, routing_key="event.payroll-manager.employee.#")
            await queue.bind(exchange, routing_key="event.payroll-manager.contract.#")

            logger.info("Audit consumer connected to RabbitMQ")
            await queue.consume(self.process_message)
        except Exception as e:
            logger.error(f"Failed to connect audit consumer: {e}")
            raise

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process():
            try:
                event_data = json.loads(message.body.decode())
                routing_key = message.routing_key

                # Parse routing key: event.payroll-manager.module.event-name
                # Convert kebab-case event name to PascalCase for backward compatibility
                parts = routing_key.split(".")
                if len(parts) >= 4:
                    event_name_kebab = ".".join(parts[3:])
                    event_type = self._kebab_to_pascal_case(event_name_kebab)
                else:
                    # Fallback for old format
                    event_type = routing_key.replace("event.", "")

                await self.handle_event(event_type, event_data)
                logger.debug(f"Processed audit event: {event_type}")
            except Exception as e:
                logger.error(f"Failed to process audit event: {e}")

    async def handle_event(self, event_type: str, event_data: dict) -> None:
        async with self.session_factory() as session:
            try:
                repository = SQLAlchemyAuditLogRepository(session)
                audit_log = self.create_audit_log_from_event(event_type, event_data)

                if audit_log:
                    await repository.save(audit_log)
                    await session.commit()
                    logger.info(f"Created audit log for {event_type}")
            except Exception as e:
                logger.error(f"Failed to create audit log for {event_type}: {e}")
                await session.rollback()

    def _kebab_to_pascal_case(self, text: str) -> str:
        """Convert kebab-case to PascalCase (e.g., employee-created-event -> EmployeeCreatedEvent)"""
        return "".join(word.capitalize() for word in text.split("-"))

    def create_audit_log_from_event(self, event_type: str, event_data: dict) -> AuditLog | None:
        try:
            if event_type == "EmployeeCreatedEvent":
                return AuditLog.create(
                    entity_type=EntityType.EMPLOYEE,
                    entity_id=event_data["employee_id"],
                    action=AuditAction.CREATED,
                    employee_id=event_data["employee_id"],
                    new_values={
                        "first_name": event_data["first_name"],
                        "last_name": event_data["last_name"],
                        "email": event_data["email"],
                        "hire_date": event_data.get("hire_date"),
                    },
                    metadata={"event_type": event_type},
                    occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
                )

            elif event_type == "EmployeeUpdatedEvent":
                return AuditLog.create(
                    entity_type=EntityType.EMPLOYEE,
                    entity_id=event_data["employee_id"],
                    action=AuditAction.UPDATED,
                    employee_id=event_data["employee_id"],
                    old_values=event_data["old_values"],
                    new_values=event_data["new_values"],
                    metadata={"event_type": event_type},
                    occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
                )

            elif event_type == "EmployeeStatusChangedEvent":
                return AuditLog.create(
                    entity_type=EntityType.EMPLOYEE,
                    entity_id=event_data["employee_id"],
                    action=AuditAction.STATUS_CHANGED,
                    employee_id=event_data["employee_id"],
                    old_values={"status": event_data["old_status"]},
                    new_values={"status": event_data["new_status"]},
                    metadata={
                        "event_type": event_type,
                        "valid_from": event_data["status_valid_from"],
                        "valid_to": event_data.get("status_valid_to"),
                        "reason": event_data.get("reason"),
                    },
                    occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
                )

            elif event_type == "ContractCreatedEvent":
                return AuditLog.create(
                    entity_type=EntityType.CONTRACT,
                    entity_id=event_data["contract_id"],
                    action=AuditAction.CREATED,
                    employee_id=event_data["employee_id"],
                    new_values={
                        "contract_type": event_data["contract_type"],
                        "rate_amount": event_data["rate_amount"],
                        "rate_currency": event_data["rate_currency"],
                        "valid_from": event_data["valid_from"],
                        "valid_to": event_data.get("valid_to"),
                    },
                    metadata={"event_type": event_type},
                    occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
                )

            elif event_type == "ContractActivatedEvent":
                return AuditLog.create(
                    entity_type=EntityType.CONTRACT,
                    entity_id=event_data["contract_id"],
                    action=AuditAction.ACTIVATED,
                    employee_id=event_data["employee_id"],
                    metadata={
                        "event_type": event_type,
                        "contract_type": event_data["contract_type"],
                        "activated_at": event_data["activated_at"],
                    },
                    occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
                )

            elif event_type == "ContractCanceledEvent":
                return AuditLog.create(
                    entity_type=EntityType.CONTRACT,
                    entity_id=event_data["contract_id"],
                    action=AuditAction.CANCELED,
                    employee_id=event_data["employee_id"],
                    metadata={
                        "event_type": event_type,
                        "contract_type": event_data["contract_type"],
                        "cancellation_reason": event_data["cancellation_reason"],
                        "canceled_at": event_data["canceled_at"],
                    },
                    occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
                )

            elif event_type == "ContractExpiredEvent":
                return AuditLog.create(
                    entity_type=EntityType.CONTRACT,
                    entity_id=event_data["contract_id"],
                    action=AuditAction.EXPIRED,
                    employee_id=event_data["employee_id"],
                    metadata={
                        "event_type": event_type,
                        "contract_type": event_data["contract_type"],
                        "expired_at": event_data["expired_at"],
                    },
                    occurred_at=datetime.fromisoformat(event_data["occurred_at"]),
                )

            else:
                logger.warning(f"Unknown event type: {event_type}")
                return None

        except Exception as e:
            logger.error(f"Failed to create audit log from event {event_type}: {e}")
            return None

    async def close(self) -> None:
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Audit consumer disconnected")


async def start_audit_consumer():
    consumer = AuditEventConsumer()
    await consumer.connect()

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        await consumer.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_audit_consumer())
