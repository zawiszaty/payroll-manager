from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
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
from app.modules.contract.domain.value_objects import ContractStatus, ContractType
from app.modules.contract.infrastructure.repository import SQLAlchemyContractRepository

router = APIRouter()


class ContractTermsResponse(BaseModel):
    contract_type: ContractType
    rate_amount: Decimal
    rate_currency: str
    valid_from: date
    valid_to: date | None
    hours_per_week: int | None
    commission_percentage: Decimal | None
    description: str | None


class ContractResponse(BaseModel):
    id: UUID
    employee_id: UUID
    terms: ContractTermsResponse
    status: ContractStatus
    version: int
    cancellation_reason: str | None
    canceled_at: date | None


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


def to_response(contract) -> ContractResponse:
    return ContractResponse(
        id=contract.id,
        employee_id=contract.employee_id,
        terms=ContractTermsResponse(
            contract_type=contract.terms.contract_type,
            rate_amount=contract.terms.rate.amount,
            rate_currency=contract.terms.rate.currency,
            valid_from=contract.terms.date_range.valid_from,
            valid_to=contract.terms.date_range.valid_to,
            hours_per_week=contract.terms.hours_per_week,
            commission_percentage=contract.terms.commission_percentage,
            description=contract.terms.description,
        ),
        status=contract.status,
        version=contract.version,
        cancellation_reason=contract.cancellation_reason,
        canceled_at=contract.canceled_at,
    )


@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
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
        return to_response(contract)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyContractRepository(db)
    handler = GetContractHandler(repository)

    query = GetContractQuery(contract_id=contract_id)
    contract = await handler.handle(query)

    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    return to_response(contract)


@router.get("/", response_model=List[ContractResponse])
async def list_contracts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyContractRepository(db)
    handler = ListContractsHandler(repository)

    query = ListContractsQuery(skip=skip, limit=limit)
    contracts = await handler.handle(query)

    return [to_response(contract) for contract in contracts]


@router.get("/employee/{employee_id}", response_model=List[ContractResponse])
async def get_contracts_by_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyContractRepository(db)
    handler = GetContractsByEmployeeHandler(repository)

    query = GetContractsByEmployeeQuery(employee_id=employee_id)
    contracts = await handler.handle(query)

    return [to_response(contract) for contract in contracts]


@router.get("/employee/{employee_id}/active", response_model=List[ContractResponse])
async def get_active_contracts(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyContractRepository(db)
    handler = GetActiveContractsHandler(repository)

    query = GetActiveContractsQuery(employee_id=employee_id)
    contracts = await handler.handle(query)

    return [to_response(contract) for contract in contracts]


@router.post("/{contract_id}/activate", response_model=ContractResponse)
async def activate_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyContractRepository(db)
    handler = ActivateContractHandler(repository)

    command = ActivateContractCommand(contract_id=contract_id)

    try:
        contract = await handler.handle(command)
        await db.commit()
        return to_response(contract)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{contract_id}/cancel", response_model=ContractResponse)
async def cancel_contract(contract_id: UUID, request: CancelContractRequest, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyContractRepository(db)
    handler = CancelContractHandler(repository)

    command = CancelContractCommand(contract_id=contract_id, reason=request.reason)

    try:
        contract = await handler.handle(command)
        await db.commit()
        return to_response(contract)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{contract_id}/expire", response_model=ContractResponse)
async def expire_contract(contract_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyContractRepository(db)
    handler = ExpireContractHandler(repository)

    command = ExpireContractCommand(contract_id=contract_id)

    try:
        contract = await handler.handle(command)
        await db.commit()
        return to_response(contract)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
