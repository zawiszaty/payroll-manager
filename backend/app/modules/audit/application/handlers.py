from app.modules.audit.application.queries import (
    GetAuditLogQuery,
    GetAuditLogsByEmployeeQuery,
    GetAuditLogsByEntityQuery,
    GetAuditTimelineQuery,
    ListAuditLogsQuery,
)
from app.modules.audit.domain.models import AuditLog
from app.modules.audit.domain.repository import AuditLogRepository


class GetAuditLogHandler:
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    async def handle(self, query: GetAuditLogQuery) -> AuditLog | None:
        return await self.repository.get_by_id(query.audit_id)


class ListAuditLogsHandler:
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    async def handle(self, query: ListAuditLogsQuery) -> list[AuditLog]:
        return await self.repository.list_all(
            page=query.page, limit=query.limit, entity_type=query.entity_type, action=query.action
        )


class GetAuditLogsByEntityHandler:
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    async def handle(self, query: GetAuditLogsByEntityQuery) -> list[AuditLog]:
        return await self.repository.get_by_entity(
            entity_type=query.entity_type,
            entity_id=query.entity_id,
            page=query.page,
            limit=query.limit,
        )


class GetAuditLogsByEmployeeHandler:
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    async def handle(self, query: GetAuditLogsByEmployeeQuery) -> list[AuditLog]:
        return await self.repository.get_by_employee(
            employee_id=query.employee_id, page=query.page, limit=query.limit
        )


class GetAuditTimelineHandler:
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    async def handle(self, query: GetAuditTimelineQuery) -> list[AuditLog]:
        return await self.repository.get_timeline(
            page=query.page,
            limit=query.limit,
            entity_type=query.entity_type,
            employee_id=query.employee_id,
            date_from=query.date_from,
            date_to=query.date_to,
        )
