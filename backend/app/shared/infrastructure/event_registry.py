"""Global event handler registry - single source of truth"""

import logging
from typing import Callable, Dict

logger = logging.getLogger(__name__)


class EventHandlerRegistry:
    """Registry for mapping event types to their handlers"""

    def __init__(self):
        self._handlers: Dict[str, Callable] = {}

    def register(self, event_type: str, handler: Callable) -> None:
        """Register a handler for a specific event type"""
        if event_type in self._handlers:
            logger.warning(f"Overwriting existing handler for event type: {event_type}")
        self._handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")

    def get_handler(self, event_type: str) -> Callable | None:
        """Get handler for an event type"""
        return self._handlers.get(event_type)

    def list_registered_events(self) -> list[str]:
        """List all registered event types"""
        return list(self._handlers.keys())


# Global registry instance - THE ONLY ONE
_global_registry = EventHandlerRegistry()


def get_event_registry() -> EventHandlerRegistry:
    """Get the global event registry"""
    return _global_registry
