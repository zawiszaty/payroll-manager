import logging
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.employee.application.commands import (
    ChangeEmployeeStatusCommand,
    CreateEmployeeCommand,
    UpdateEmployeeCommand,
)
from app.modules.employee.application.handlers import (
    ChangeEmployeeStatusHandler,
    CreateEmployeeHandler,
    GetEmployeeHandler,
    ListEmployeesHandler,
    UpdateEmployeeHandler,
)
from app.modules.employee.application.queries import GetEmployeeQuery, ListEmployeesQuery
from app.modules.employee.domain.value_objects import EmploymentStatusType
from app.modules.employee.infrastructure.read_model import EmployeeReadModel
from app.modules.employee.infrastructure.repository import SQLAlchemyEmployeeRepository
from app.modules.employee.presentation.views import EmployeeDetailView, EmployeeListView
from app.shared.infrastructure.pagination import PaginatedResponse, create_paginated_response

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateEmployeeRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    hire_date: date
    phone: str | None = None
    date_of_birth: date | None = None


class UpdateEmployeeRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    date_of_birth: date | None = None


class ChangeStatusRequest(BaseModel):
    new_status: EmploymentStatusType
    effective_date: date
    reason: str | None = None


@router.post("/", response_model=EmployeeDetailView, status_code=status.HTTP_201_CREATED)
async def create_employee(request: CreateEmployeeRequest, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyEmployeeRepository(db)
    handler = CreateEmployeeHandler(repository)

    command = CreateEmployeeCommand(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        hire_date=request.hire_date,
        phone=request.phone,
        date_of_birth=request.date_of_birth,
    )

    try:
        employee = await handler.handle(command)
        await db.commit()

        # Dispatch events AFTER successful commit
        from app.shared.domain.events import get_event_dispatcher

        dispatcher = get_event_dispatcher()
        events = employee.get_domain_events()
        for event in events:
            try:
                await dispatcher.dispatch(event)
            except Exception as dispatch_error:
                # Log but don't fail the request - event dispatch is async
                logger.error(
                    f"Failed to dispatch event {event.__class__.__name__}: {dispatch_error}"
                )
        employee.clear_domain_events()

        # Fetch from ReadModel after write
        read_model = EmployeeReadModel(db)
        view = await read_model.get_by_id(employee.id)
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{employee_id}", response_model=EmployeeDetailView)
async def get_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    read_model = EmployeeReadModel(db)
    handler = GetEmployeeHandler(read_model)

    query = GetEmployeeQuery(employee_id=employee_id)
    view = await handler.handle(query)

    if not view:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    return view


@router.get("/", response_model=PaginatedResponse[EmployeeListView])
async def list_employees(
    request: Request,
    page: int = 1,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

    skip = (page - 1) * limit

    read_model = EmployeeReadModel(db)
    handler = ListEmployeesHandler(read_model)

    query = ListEmployeesQuery(skip=skip, limit=limit)
    items, total_count = await handler.handle(query)

    base_url = str(request.url).split("?")[0]
    return create_paginated_response(
        items=items,
        total_items=total_count,
        page=page,
        limit=limit,
        base_url=base_url,
    )


@router.put("/{employee_id}", response_model=EmployeeDetailView)
async def update_employee(
    employee_id: UUID, request: UpdateEmployeeRequest, db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyEmployeeRepository(db)
    handler = UpdateEmployeeHandler(repository)

    command = UpdateEmployeeCommand(
        employee_id=employee_id,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        phone=request.phone,
        date_of_birth=request.date_of_birth,
    )

    try:
        employee = await handler.handle(command)
        await db.commit()

        # Dispatch events AFTER successful commit
        from app.shared.domain.events import get_event_dispatcher

        dispatcher = get_event_dispatcher()
        events = employee.get_domain_events()
        for event in events:
            try:
                await dispatcher.dispatch(event)
            except Exception as dispatch_error:
                # Log but don't fail the request - event dispatch is async
                logger.error(
                    f"Failed to dispatch event {event.__class__.__name__}: {dispatch_error}"
                )
        employee.clear_domain_events()

        # Fetch from ReadModel after write
        read_model = EmployeeReadModel(db)
        view = await read_model.get_by_id(employee.id)
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{employee_id}/status", response_model=EmployeeDetailView)
async def change_employee_status(
    employee_id: UUID, request: ChangeStatusRequest, db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyEmployeeRepository(db)
    handler = ChangeEmployeeStatusHandler(repository)

    command = ChangeEmployeeStatusCommand(
        employee_id=employee_id,
        new_status=request.new_status,
        effective_date=request.effective_date,
        reason=request.reason,
    )

    try:
        employee = await handler.handle(command)
        await db.commit()

        read_model = EmployeeReadModel(db)
        view = await read_model.get_by_id(employee.id)
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
