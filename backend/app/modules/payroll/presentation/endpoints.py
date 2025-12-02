from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.auth.infrastructure.dependencies import get_current_active_user
from app.modules.payroll.application.commands import (
    ApprovePayrollCommand,
    CalculatePayrollCommand,
    CreatePayrollCommand,
    MarkPayrollAsPaidCommand,
    ProcessPayrollCommand,
)
from app.modules.payroll.application.handlers import (
    ApprovePayrollHandler,
    CalculatePayrollHandler,
    CreatePayrollHandler,
    GetPayrollHandler,
    ListPayrollsByEmployeeHandler,
    ListPayrollsHandler,
    MarkPayrollAsPaidHandler,
    ProcessPayrollHandler,
)
from app.modules.payroll.application.queries import (
    GetPayrollQuery,
    ListPayrollsByEmployeeQuery,
    ListPayrollsQuery,
)
from app.modules.payroll.domain.services import PayrollCalculationService
from app.modules.payroll.domain.value_objects import PayrollPeriodType
from app.modules.payroll.infrastructure.adapters import (
    PayrollDataGatheringAdapter,
    PayrollValidationAdapter,
)
from app.modules.payroll.infrastructure.read_model import PayrollReadModel
from app.modules.payroll.infrastructure.repository import SQLAlchemyPayrollRepository
from app.modules.payroll.presentation.views import PayrollDetailView, PayrollListView
from app.shared.infrastructure.pagination import PaginatedResponse, create_paginated_response

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class CreatePayrollRequest(BaseModel):
    employee_id: UUID
    period_type: PayrollPeriodType
    period_start_date: date
    period_end_date: date
    notes: str | None = None


class CalculatePayrollRequest(BaseModel):
    working_days: int = 22


class ApprovePayrollRequest(BaseModel):
    approved_by: UUID


class MarkAsPaidRequest(BaseModel):
    payment_reference: str


@router.post("/", response_model=PayrollDetailView, status_code=status.HTTP_201_CREATED)
async def create_payroll(request: CreatePayrollRequest, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyPayrollRepository(db)
    validation_adapter = PayrollValidationAdapter(db)
    handler = CreatePayrollHandler(repository, validation_adapter)

    command = CreatePayrollCommand(
        employee_id=request.employee_id,
        period_type=request.period_type,
        period_start_date=request.period_start_date,
        period_end_date=request.period_end_date,
        notes=request.notes,
    )

    try:
        payroll = await handler.handle(command)

        # Query the read model BEFORE committing to avoid expired object issues
        read_model = PayrollReadModel(db)
        view = await read_model.get_by_id(payroll.id)

        await db.commit()
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{payroll_id}", response_model=PayrollDetailView)
async def get_payroll(payroll_id: UUID, db: AsyncSession = Depends(get_db)):
    read_model = PayrollReadModel(db)
    handler = GetPayrollHandler(read_model)

    query = GetPayrollQuery(payroll_id=payroll_id)
    view = await handler.handle(query)

    if not view:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payroll not found")

    return view


@router.get("/", response_model=PaginatedResponse[PayrollListView])
async def list_payrolls(
    request: Request,
    page: int = 1,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

    read_model = PayrollReadModel(db)
    handler = ListPayrollsHandler(read_model)

    query = ListPayrollsQuery(page=page, limit=limit)
    items, total_count = await handler.handle(query)

    base_url = str(request.url).split("?")[0]
    return create_paginated_response(
        items=items,
        total_items=total_count,
        page=page,
        limit=limit,
        base_url=base_url,
    )


@router.get("/employee/{employee_id}", response_model=PaginatedResponse[PayrollListView])
async def list_payrolls_by_employee(
    employee_id: UUID,
    request: Request,
    page: int = 1,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")

    read_model = PayrollReadModel(db)
    handler = ListPayrollsByEmployeeHandler(read_model)

    query = ListPayrollsByEmployeeQuery(employee_id=employee_id, page=page, limit=limit)
    items, total_count = await handler.handle(query)

    base_url = str(request.url).split("?")[0]
    return create_paginated_response(
        items=items,
        total_items=total_count,
        page=page,
        limit=limit,
        base_url=base_url,
    )


@router.post("/{payroll_id}/calculate", response_model=PayrollDetailView)
async def calculate_payroll(
    payroll_id: UUID, request: CalculatePayrollRequest, db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyPayrollRepository(db)
    data_adapter = PayrollDataGatheringAdapter(db)
    calculation_service = PayrollCalculationService(data_adapter)
    handler = CalculatePayrollHandler(repository, calculation_service)

    command = CalculatePayrollCommand(payroll_id=payroll_id, working_days=request.working_days)

    try:
        payroll = await handler.handle(command)

        # Query the read model BEFORE committing to avoid expired object issues
        read_model = PayrollReadModel(db)
        view = await read_model.get_by_id(payroll.id)

        await db.commit()
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{payroll_id}/approve", response_model=PayrollDetailView)
async def approve_payroll(
    payroll_id: UUID, request: ApprovePayrollRequest, db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyPayrollRepository(db)
    handler = ApprovePayrollHandler(repository)

    command = ApprovePayrollCommand(payroll_id=payroll_id, approved_by=request.approved_by)

    try:
        payroll = await handler.handle(command)

        # Query the read model BEFORE committing to avoid expired object issues
        read_model = PayrollReadModel(db)
        view = await read_model.get_by_id(payroll.id)

        await db.commit()
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{payroll_id}/process", response_model=PayrollDetailView)
async def process_payroll(payroll_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyPayrollRepository(db)
    handler = ProcessPayrollHandler(repository)

    command = ProcessPayrollCommand(payroll_id=payroll_id)

    try:
        payroll = await handler.handle(command)

        # Query the read model BEFORE committing to avoid expired object issues
        read_model = PayrollReadModel(db)
        view = await read_model.get_by_id(payroll.id)

        await db.commit()
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{payroll_id}/mark-paid", response_model=PayrollDetailView)
async def mark_payroll_as_paid(
    payroll_id: UUID, request: MarkAsPaidRequest, db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyPayrollRepository(db)
    handler = MarkPayrollAsPaidHandler(repository)

    command = MarkPayrollAsPaidCommand(
        payroll_id=payroll_id, payment_reference=request.payment_reference
    )

    try:
        payroll = await handler.handle(command)

        # Query the read model BEFORE committing to avoid expired object issues
        read_model = PayrollReadModel(db)
        view = await read_model.get_by_id(payroll.id)

        await db.commit()
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
