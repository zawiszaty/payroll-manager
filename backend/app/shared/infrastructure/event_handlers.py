"""
Central registry for all event handlers across all modules.
Each module should register its event handlers here.
"""

import logging

from app.shared.infrastructure.event_registry import get_event_registry

logger = logging.getLogger(__name__)


def register_all_handlers() -> None:
    """
    Register all event handlers from all modules.
    This function should be called on consumer startup.
    """
    logger.info("Registering event handlers from all modules...")

    registry = get_event_registry()

    # Register employee module handlers (emit audit events)
    from app.modules.employee.infrastructure.event_handlers import (
        register_employee_audit_handlers,
    )

    register_employee_audit_handlers(registry)

    # Register contract module handlers (emit audit events)
    from app.modules.contract.infrastructure.event_handlers import (
        register_contract_audit_handlers,
    )

    register_contract_audit_handlers(registry)

    # Register audit module handlers (consume audit events)
    from app.modules.audit.infrastructure.event_handlers import register_audit_handlers

    register_audit_handlers(registry)

    # Register reporting module handlers
    from app.modules.reporting.infrastructure.event_handlers import register_reporting_handlers

    register_reporting_handlers(registry)

    logger.info(f"Total registered event types: {len(registry.list_registered_events())}")
