from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.contract.application.commands import (
    ActivateContractCommand,
    CancelContractCommand,
    CreateContractCommand,
    ExpireContractCommand,
)
from app.modules.contract.application.handlers import (
    ActivateContractHandler,
    CancelContractHandler,
    CreateContractHandler,
    ExpireContractHandler,
    GetActiveContractsHandler,
    GetContractHandler,
    GetContractsByEmployeeHandler,
    ListContractsHandler,
)
from app.modules.contract.application.queries import (
    GetActiveContractsQuery,
    GetContractQuery,
    GetContractsByEmployeeQuery,
    ListContractsQuery,
)
from app.modules.contract.domain.value_objects import ContractType
from app.modules.contract.infrastructure.read_model import ContractReadModel
from app.modules.contract.infrastructure.repository import SQLAlchemyContractRepository
from app.modules.contract.presentation.views import (
    ContractDetailView,
    ContractListResponse,
    ContractListView,
)
from app.shared.infrastructure.pagination import PaginatedResponse, create_paginated_response

router = APIRouter()


class CreateContractRequest(BaseModel):
    employee_id: UUID
    contract_type: ContractType
    rate_amount: Decimal
    rate_currency: str = "USD"
    valid_from: date
    valid_to: date | None = None
    hours_per_week: int | None = None
    commission_percentage: Decimal | None = None
    description: str | None = None


class ActivateContractRequest(BaseModel):
    pass


class CancelContractRequest(BaseModel):
    reason: str


@router.post("/", response_model=ContractDetailView, status_code=status.HTTP_201_CREATED)
async def create_contract(request: CreateContractRequest, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyContractRepository(db)
    handler = CreateContractHandler(repository)

    command = CreateContractCommand(
        employee_id=request.employee_id,
        contract_type=request.contract_type,
        rate_amount=request.rate_amount,
        rate_currency=request.rate_currency,
        valid_from=request.valid_from,
        valid_to=request.valid_to,
        hours_per_week=request.hours_per_week,
        commission_percentage=request.commission_percentage,
        description=request.description,
    )

    try:
        contract = await handler.handle(command)
        await db.commit()
        # Fetch from ReadModel after write
        read_model = ContractReadModel(db)
        view = await read_model.get_by_id(contract.id)
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{contract_id}", response_model=ContractDetailView)
async def get_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    read_model = ContractReadModel(db)
    handler = GetContractHandler(read_model)

    query = GetContractQuery(contract_id=contract_id)
    view = await handler.handle(query)

    if not view:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    return view


@router.get("/", response_model=PaginatedResponse[ContractListView])
async def list_contracts(
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

    read_model = ContractReadModel(db)
    handler = ListContractsHandler(read_model)

    query = ListContractsQuery(skip=skip, limit=limit)
    items, total_count = await handler.handle(query)

    base_url = str(request.url).split("?")[0]
    return create_paginated_response(
        items=items,
        total_items=total_count,
        page=page,
        limit=limit,
        base_url=base_url,
    )


@router.get("/employee/{employee_id}", response_model=ContractListResponse)
async def get_contracts_by_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    read_model = ContractReadModel(db)
    handler = GetContractsByEmployeeHandler(read_model)

    query = GetContractsByEmployeeQuery(employee_id=employee_id)
    views = await handler.handle(query)

    return ContractListResponse(items=views, total=len(views))


@router.get("/employee/{employee_id}/active", response_model=ContractListResponse)
async def get_active_contracts(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    read_model = ContractReadModel(db)
    handler = GetActiveContractsHandler(read_model)

    query = GetActiveContractsQuery(employee_id=employee_id)
    views = await handler.handle(query)

    return ContractListResponse(items=views, total=len(views))


@router.post("/{contract_id}/activate", response_model=ContractDetailView)
async def activate_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyContractRepository(db)
    handler = ActivateContractHandler(repository)

    command = ActivateContractCommand(contract_id=contract_id)

    try:
        contract = await handler.handle(command)
        await db.commit()
        # Fetch from ReadModel after write
        read_model = ContractReadModel(db)
        view = await read_model.get_by_id(contract.id)
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{contract_id}/cancel", response_model=ContractDetailView)
async def cancel_contract(
    contract_id: UUID, request: CancelContractRequest, db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyContractRepository(db)
    handler = CancelContractHandler(repository)

    command = CancelContractCommand(contract_id=contract_id, reason=request.reason)

    try:
        contract = await handler.handle(command)
        await db.commit()
        read_model = ContractReadModel(db)
        view = await read_model.get_by_id(contract.id)
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{contract_id}/expire", response_model=ContractDetailView)
async def expire_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyContractRepository(db)
    handler = ExpireContractHandler(repository)

    command = ExpireContractCommand(contract_id=contract_id)

    try:
        contract = await handler.handle(command)
        await db.commit()
        read_model = ContractReadModel(db)
        view = await read_model.get_by_id(contract.id)
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
