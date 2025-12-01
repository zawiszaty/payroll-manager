import json
import logging
from typing import Any

import aio_pika
from aio_pika import Connection, ExchangeType, Message

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RabbitMQPublisher:
    _instance: "RabbitMQPublisher | None" = None
    _connection: Connection | None = None
    _channel: Any | None = None
    _exchange: Any | None = None

    def __new__(cls) -> "RabbitMQPublisher":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        if self._connection is None or self._connection.is_closed:
            import asyncio

            max_retries = 5
            retry_delay = 2

            for attempt in range(max_retries):
                try:
                    self._connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
                    self._channel = await self._connection.channel()
                    self._exchange = await self._channel.declare_exchange(
                        "domain_events", ExchangeType.TOPIC, durable=True
                    )
                    logger.info("RabbitMQ publisher connected")
                    return
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}"
                        )
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(
                            f"Failed to connect to RabbitMQ after {max_retries} attempts: {e}"
                        )
                        raise

    async def publish_event(self, event_type: str, event_data: dict, module: str = None) -> None:
        try:
            if self._exchange is None:
                logger.warning("Exchange is None, connecting...")
                await self.connect()

            message_body = json.dumps(event_data, default=str)
            message = Message(
                body=message_body.encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            # Auto-detect module from event type if not provided
            # e.g., "EmployeeCreatedEvent" -> "employee.employee-created-event"
            if module is None:
                # Convert camelCase to kebab-case and extract module
                module = self._extract_module_from_event(event_type)

            # Format: event.payroll-manager.module.event-name
            event_name = self._to_kebab_case(event_type)
            routing_key = f"event.payroll-manager.{module}.{event_name}"

            await self._exchange.publish(message, routing_key=routing_key)
            logger.debug(f"Published event: {routing_key}")
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")

    def _extract_module_from_event(self, event_type: str) -> str:
        """Extract module name from event type (e.g., EmployeeCreatedEvent -> employee)"""
        # Common module prefixes
        if "Employee" in event_type:
            return "employee"
        elif "Contract" in event_type:
            return "contract"
        elif "Report" in event_type:
            return "reporting"
        elif "Audit" in event_type:
            return "audit"
        elif "Payroll" in event_type:
            return "payroll"
        elif "Absence" in event_type:
            return "absence"
        elif "Timesheet" in event_type:
            return "timesheet"
        elif "Compensation" in event_type:
            return "compensation"
        else:
            return "unknown"

    def _to_kebab_case(self, text: str) -> str:
        """Convert CamelCase to kebab-case"""
        import re

        # Insert hyphens before uppercase letters and convert to lowercase
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", text)
        return re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).lower()

    async def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ publisher disconnected")


def get_rabbitmq_publisher() -> RabbitMQPublisher:
    return RabbitMQPublisher()
