from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.employee.api.views import EmployeeDetailView, EmployeeListView
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


@router.get("/", response_model=List[EmployeeListView])
async def list_employees(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    read_model = EmployeeReadModel(db)
    handler = ListEmployeesHandler(read_model)

    query = ListEmployeesQuery(skip=skip, limit=limit)
    views = await handler.handle(query)

    return views


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
