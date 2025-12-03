from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.application.queries import (
    GetAuditLogQuery,
    GetAuditLogsByEmployeeQuery,
    GetAuditLogsByEntityQuery,
    GetAuditTimelineQuery,
    ListAuditLogsQuery,
)
from app.modules.audit.infrastructure.read_model import AuditLogReadModel
from app.modules.audit.presentation.views import AuditLogResponse


class GetAuditLogHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: GetAuditLogQuery) -> AuditLogResponse | None:
        read_model = AuditLogReadModel(self.session)
        return await read_model.get_by_id(query.audit_id)


class ListAuditLogsHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: ListAuditLogsQuery) -> tuple[list[AuditLogResponse], int]:
        skip = (query.page - 1) * query.limit
        read_model = AuditLogReadModel(self.session)
        return await read_model.list(
            skip=skip, limit=query.limit, entity_type=query.entity_type, action=query.action
        )


class GetAuditLogsByEntityHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: GetAuditLogsByEntityQuery) -> tuple[list[AuditLogResponse], int]:
        skip = (query.page - 1) * query.limit
        read_model = AuditLogReadModel(self.session)
        return await read_model.get_by_entity(
            entity_type=query.entity_type, entity_id=query.entity_id, skip=skip, limit=query.limit
        )


class GetAuditLogsByEmployeeHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(
        self, query: GetAuditLogsByEmployeeQuery
    ) -> tuple[list[AuditLogResponse], int]:
        skip = (query.page - 1) * query.limit
        read_model = AuditLogReadModel(self.session)
        return await read_model.get_by_employee(
            employee_id=query.employee_id, skip=skip, limit=query.limit
        )


class GetAuditTimelineHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: GetAuditTimelineQuery) -> tuple[list[AuditLogResponse], int]:
        skip = (query.page - 1) * query.limit
        read_model = AuditLogReadModel(self.session)
        return await read_model.get_timeline(
            skip=skip,
            limit=query.limit,
            entity_type=query.entity_type,
            employee_id=query.employee_id,
            date_from=query.date_from,
            date_to=query.date_to,
        )
