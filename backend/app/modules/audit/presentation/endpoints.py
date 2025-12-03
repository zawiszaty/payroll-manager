from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.audit.application.handlers import (
    GetAuditLogHandler,
    GetAuditLogsByEmployeeHandler,
    GetAuditLogsByEntityHandler,
    GetAuditTimelineHandler,
    ListAuditLogsHandler,
)
from app.modules.audit.application.queries import (
    GetAuditLogQuery,
    GetAuditLogsByEmployeeQuery,
    GetAuditLogsByEntityQuery,
    GetAuditTimelineQuery,
    ListAuditLogsQuery,
)
from app.modules.audit.domain.value_objects import AuditAction, EntityType
from app.modules.audit.presentation.views import AuditLogListResponse, AuditLogResponse
from app.modules.auth.infrastructure.dependencies import get_current_active_user

router = APIRouter(dependencies=[Depends(get_current_active_user)])


@router.get("/", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> AuditLogListResponse:
    try:
        entity_type_enum = EntityType(entity_type) if entity_type else None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid entity_type: {entity_type}"
        )

    try:
        action_enum = AuditAction(action) if action else None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid action: {action}"
        )

    handler = ListAuditLogsHandler(db)
    query = ListAuditLogsQuery(
        page=page, limit=limit, entity_type=entity_type_enum, action=action_enum
    )
    items, total_count = await handler.handle(query)

    return AuditLogListResponse(items=items, total=total_count, page=page, limit=limit)


@router.get("/entity/{entity_type}/{entity_id}", response_model=AuditLogListResponse)
async def get_audit_logs_by_entity(
    entity_type: str,
    entity_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> AuditLogListResponse:
    try:
        entity_type_enum = EntityType(entity_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid entity type: {entity_type}"
        )

    handler = GetAuditLogsByEntityHandler(db)
    query = GetAuditLogsByEntityQuery(
        entity_type=entity_type_enum, entity_id=entity_id, page=page, limit=limit
    )
    items, total_count = await handler.handle(query)

    return AuditLogListResponse(items=items, total=total_count, page=page, limit=limit)


@router.get("/employee/{employee_id}", response_model=AuditLogListResponse)
async def get_audit_logs_by_employee(
    employee_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> AuditLogListResponse:
    handler = GetAuditLogsByEmployeeHandler(db)
    query = GetAuditLogsByEmployeeQuery(employee_id=employee_id, page=page, limit=limit)
    items, total_count = await handler.handle(query)

    return AuditLogListResponse(items=items, total=total_count, page=page, limit=limit)


@router.get("/timeline", response_model=AuditLogListResponse)
async def get_audit_timeline(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    entity_type: Optional[str] = None,
    employee_id: Optional[UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
) -> AuditLogListResponse:
    try:
        entity_type_enum = EntityType(entity_type) if entity_type else None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid entity_type: {entity_type}"
        )

    handler = GetAuditTimelineHandler(db)
    query = GetAuditTimelineQuery(
        page=page,
        limit=limit,
        entity_type=entity_type_enum,
        employee_id=employee_id,
        date_from=date_from,
        date_to=date_to,
    )
    items, total_count = await handler.handle(query)

    return AuditLogListResponse(items=items, total=total_count, page=page, limit=limit)


@router.get("/{audit_id}", response_model=AuditLogResponse)
async def get_audit_log(audit_id: UUID, db: AsyncSession = Depends(get_db)) -> AuditLogResponse:
    handler = GetAuditLogHandler(db)
    query = GetAuditLogQuery(audit_id=audit_id)
    audit_log = await handler.handle(query)

    if not audit_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")

    return audit_log
