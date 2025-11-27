from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
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
from app.modules.employee.infrastructure.repository import SQLAlchemyEmployeeRepository

router = APIRouter()


class EmploymentStatusResponse(BaseModel):
    status_type: EmploymentStatusType
    valid_from: date
    valid_to: date | None
    reason: str | None


class EmployeeResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None
    date_of_birth: date | None
    hire_date: date | None
    statuses: List[EmploymentStatusResponse]


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


def to_response(employee) -> EmployeeResponse:
    return EmployeeResponse(
        id=employee.id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        phone=employee.phone,
        date_of_birth=employee.date_of_birth,
        hire_date=employee.hire_date,
        statuses=[
            EmploymentStatusResponse(
                status_type=s.status_type,
                valid_from=s.date_range.valid_from,
                valid_to=s.date_range.valid_to,
                reason=s.reason,
            )
            for s in employee.statuses
        ],
    )


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
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
        return to_response(employee)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyEmployeeRepository(db)
    handler = GetEmployeeHandler(repository)

    query = GetEmployeeQuery(employee_id=employee_id)
    employee = await handler.handle(query)

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    return to_response(employee)


@router.get("/", response_model=List[EmployeeResponse])
async def list_employees(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyEmployeeRepository(db)
    handler = ListEmployeesHandler(repository)

    query = ListEmployeesQuery(skip=skip, limit=limit)
    employees = await handler.handle(query)

    return [to_response(emp) for emp in employees]


@router.put("/{employee_id}", response_model=EmployeeResponse)
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
        return to_response(employee)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{employee_id}/status", response_model=EmployeeResponse)
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
        return to_response(employee)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
