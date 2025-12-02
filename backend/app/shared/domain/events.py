import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class DomainEvent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_id: UUID = Field(default_factory=uuid4)
    changed_by: UUID | None = Field(default=None)


class AsyncEventDispatcher:
    _instance: "AsyncEventDispatcher | None" = None

    def __new__(cls) -> "AsyncEventDispatcher":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def _handle_task_exception(task: asyncio.Task, event_type: str, event_id: UUID) -> None:
        """Handle exceptions from background event publishing tasks."""
        try:
            exception = task.exception()
            if exception is not None:
                logger.error(
                    f"Event publishing failed - event_type: {event_type}, "
                    f"event_id: {event_id}, error: {exception}",
                    exc_info=exception,
                )
        except asyncio.CancelledError:
            logger.warning(
                f"Event publishing task cancelled - event_type: {event_type}, event_id: {event_id}"
            )
        except Exception as e:
            logger.error(
                f"Error handling task exception - event_type: {event_type}, event_id: {event_id}: {e}"
            )

    async def dispatch(self, event: DomainEvent) -> None:
        try:
            from app.shared.infrastructure.context import get_current_user_id
            from app.shared.infrastructure.rabbitmq import get_rabbitmq_publisher

            # Set changed_by from context if not already set
            if event.changed_by is None:
                current_user_id = get_current_user_id()
                event.changed_by = current_user_id
                logger.info(f"Set changed_by from context: {current_user_id}")

            publisher = get_rabbitmq_publisher()
            event_type = event.__class__.__name__
            event_data = event.model_dump(mode="json")
            event_id = event.event_id

            logger.info(
                f"Dispatching event: {event_type} (id: {event_id}) with changed_by={event_data.get('changed_by')}"
            )

            # Create task for async publishing with proper exception handling
            task = asyncio.create_task(publisher.publish_event(event_type, event_data))
            task.add_done_callback(lambda t: self._handle_task_exception(t, event_type, event_id))
        except Exception as e:
            logger.error(f"Failed to dispatch event: {e}")


def get_event_dispatcher() -> AsyncEventDispatcher:
    return AsyncEventDispatcher()
