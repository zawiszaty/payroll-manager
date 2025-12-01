import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DomainEvent(BaseModel):
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_id: UUID = Field(default_factory=lambda: UUID(int=0))

    class Config:
        arbitrary_types_allowed = True


class AsyncEventDispatcher:
    _instance: "AsyncEventDispatcher | None" = None

    def __new__(cls) -> "AsyncEventDispatcher":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def dispatch(self, event: DomainEvent) -> None:
        try:
            from app.shared.infrastructure.rabbitmq import get_rabbitmq_publisher

            publisher = get_rabbitmq_publisher()
            event_type = event.__class__.__name__
            event_data = event.model_dump(mode="json")

            logger.debug(f"Dispatching event: {event_type}")
            # Create task for async publishing to not block
            asyncio.create_task(publisher.publish_event(event_type, event_data))
        except Exception as e:
            logger.error(f"Failed to dispatch event: {e}")


def get_event_dispatcher() -> AsyncEventDispatcher:
    return AsyncEventDispatcher()
