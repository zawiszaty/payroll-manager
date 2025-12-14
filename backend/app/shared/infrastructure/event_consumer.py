"""
Unified Event Consumer for all domain events in the application.
This consumer handles events from all modules through a centralized registry.
"""

import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, AbstractRobustConnection

from app.config import get_settings
from app.shared.infrastructure.event_registry import EventHandlerRegistry, get_event_registry

logger = logging.getLogger(__name__)
settings = get_settings()


class UnifiedEventConsumer:
    """
    Unified consumer that handles all domain events from all modules.
    Routes events to appropriate handlers based on event type.
    """

    def __init__(self, registry: EventHandlerRegistry | None = None):
        self.registry = registry or get_event_registry()
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None

    async def connect(self) -> None:
        """Connect to RabbitMQ and set up queue bindings"""
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            exchange = await self.channel.declare_exchange(
                "domain_events", aio_pika.ExchangeType.TOPIC, durable=True
            )

            queue = await self.channel.declare_queue("payroll_events", durable=True)

            # Bind to all payroll-manager events using wildcard
            # Format: event.payroll-manager.*.* will catch all events from all modules
            await queue.bind(exchange, routing_key="event.payroll-manager.#")

            logger.info("Unified event consumer connected to RabbitMQ")
            logger.info(f"Registered event types: {self.registry.list_registered_events()}")

            await queue.consume(self.process_message)
        except Exception as e:
            logger.error(f"Failed to connect unified event consumer: {e}")
            raise

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        """Process incoming message and route to appropriate handler"""
        async with message.process():
            try:
                event_data = json.loads(message.body.decode())
                routing_key = message.routing_key

                # Parse routing key: event.payroll-manager.module.event-name
                if routing_key is None:
                    logger.warning("Routing key is None")
                    return

                parts = routing_key.split(".")
                if len(parts) < 4:
                    logger.warning(f"Invalid routing key format: {routing_key}")
                    return

                # Extract event type from routing key
                # event.payroll-manager.audit.employee-created
                # -> audit.employee-created
                module = parts[2]
                event_name = ".".join(parts[3:])
                event_type = f"{module}.{event_name}"

                logger.info(f"Received event: {event_type} (routing key: {routing_key})")
                logger.info(f"Available handlers: {self.registry.list_registered_events()}")

                # Get handler for this event type
                handler = self.registry.get_handler(event_type)

                if handler:
                    await handler(event_data)
                    logger.info(f"Successfully processed event: {event_type}")
                else:
                    logger.warning(f"No handler registered for event type: {event_type}")
                    logger.warning(
                        f"Registry has {len(self.registry.list_registered_events())} handlers"
                    )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode message body: {e}")
            except Exception as e:
                logger.error(f"Failed to process event: {e}", exc_info=True)

    async def close(self) -> None:
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Unified event consumer disconnected")


async def start_unified_consumer():
    """Start the unified event consumer"""
    # Import all event handlers to ensure they're registered
    from app.shared.infrastructure.event_handlers import register_all_handlers

    # Register all handlers BEFORE creating consumer
    register_all_handlers()

    registry = get_event_registry()
    logger.info(f"Registry after registration: {registry.list_registered_events()}")

    # Create consumer without passing registry - it will use global one
    consumer = UnifiedEventConsumer()
    logger.info(f"Consumer registry: {consumer.registry.list_registered_events()}")
    await consumer.connect()

    # Start the payroll scheduler for month-end processing
    from app.modules.payroll.infrastructure.scheduler import start_scheduler

    await start_scheduler()
    logger.info("Payroll scheduler started")

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        from app.modules.payroll.infrastructure.scheduler import stop_scheduler

        await stop_scheduler()
        await consumer.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_unified_consumer())
