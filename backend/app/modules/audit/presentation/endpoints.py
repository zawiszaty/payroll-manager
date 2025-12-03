from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.audit.domain.value_objects import AuditAction, EntityType
from app.modules.audit.infrastructure.read_model import AuditLogReadModel
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

    skip = (page - 1) * limit
    read_model = AuditLogReadModel(db)
    items, total_count = await read_model.list(
        skip=skip, limit=limit, entity_type=entity_type_enum, action=action_enum
    )

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

    skip = (page - 1) * limit
    read_model = AuditLogReadModel(db)
    items, total_count = await read_model.get_by_entity(
        entity_type=entity_type_enum, entity_id=entity_id, skip=skip, limit=limit
    )

    return AuditLogListResponse(items=items, total=total_count, page=page, limit=limit)


@router.get("/employee/{employee_id}", response_model=AuditLogListResponse)
async def get_audit_logs_by_employee(
    employee_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> AuditLogListResponse:
    skip = (page - 1) * limit
    read_model = AuditLogReadModel(db)
    items, total_count = await read_model.get_by_employee(
        employee_id=employee_id, skip=skip, limit=limit
    )

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

    skip = (page - 1) * limit
    read_model = AuditLogReadModel(db)
    items, total_count = await read_model.get_timeline(
        skip=skip,
        limit=limit,
        entity_type=entity_type_enum,
        employee_id=employee_id,
        date_from=date_from,
        date_to=date_to,
    )

    return AuditLogListResponse(items=items, total=total_count, page=page, limit=limit)


@router.get("/{audit_id}", response_model=AuditLogResponse)
async def get_audit_log(audit_id: UUID, db: AsyncSession = Depends(get_db)) -> AuditLogResponse:
    read_model = AuditLogReadModel(db)
    audit_log = await read_model.get_by_id(audit_id)

    if not audit_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")

    return audit_log
