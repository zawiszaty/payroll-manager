from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.shared.infrastructure.pagination import PaginatedResponse, create_paginated_response
from app.modules.compensation.api.views import (
    BonusListResponse,
    BonusView,
    RateListResponse,
    RateView,
)
from app.modules.compensation.application.commands import CreateBonusCommand, CreateRateCommand
from app.modules.compensation.application.handlers import (
    CreateBonusHandler,
    CreateRateHandler,
    GetActiveRateHandler,
    GetBonusesByEmployeeHandler,
    GetBonusHandler,
    GetRateHandler,
    GetRatesByEmployeeHandler,
    ListBonusesHandler,
    ListRatesHandler,
)
from app.modules.compensation.application.queries import (
    GetActiveRateQuery,
    GetBonusesByEmployeeQuery,
    GetBonusQuery,
    GetRateQuery,
    GetRatesByEmployeeQuery,
    ListBonusesQuery,
    ListRatesQuery,
)
from app.modules.compensation.domain.value_objects import BonusType, RateType
from app.modules.compensation.infrastructure.read_model import BonusReadModel, RateReadModel
from app.modules.compensation.infrastructure.repository import (
    SQLAlchemyBonusRepository,
    SQLAlchemyRateRepository,
)

router = APIRouter()


class CreateRateRequest(BaseModel):
    employee_id: UUID
    rate_type: RateType
    amount: Decimal
    currency: str = "USD"
    valid_from: date
    valid_to: date | None = None
    description: str | None = None


class CreateBonusRequest(BaseModel):
    employee_id: UUID
    bonus_type: BonusType
    amount: Decimal
    currency: str = "USD"
    payment_date: date
    description: str | None = None


@router.post("/rates/", response_model=RateView, status_code=status.HTTP_201_CREATED)
async def create_rate(request: CreateRateRequest, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyRateRepository(db)
    handler = CreateRateHandler(repository)

    command = CreateRateCommand(
        employee_id=request.employee_id,
        rate_type=request.rate_type,
        amount=request.amount,
        currency=request.currency,
        valid_from=request.valid_from,
        valid_to=request.valid_to,
        description=request.description,
    )

    try:
        rate = await handler.handle(command)
        await db.commit()
        # Fetch from ReadModel after write
        read_model = RateReadModel(db)
        view = await read_model.get_by_id(rate.id)
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/rates/{rate_id}", response_model=RateView)
async def get_rate(rate_id: UUID, db: AsyncSession = Depends(get_db)):
    read_model = RateReadModel(db)
    handler = GetRateHandler(read_model)

    query = GetRateQuery(rate_id=rate_id)
    rate = await handler.handle(query)

    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found")

    return rate


@router.get("/rates/", response_model=PaginatedResponse[RateView])
async def list_rates(
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

    read_model = RateReadModel(db)
    handler = ListRatesHandler(read_model)

    query = ListRatesQuery(skip=skip, limit=limit)
    items, total_count = await handler.handle(query)

    base_url = str(request.url).split("?")[0]
    return create_paginated_response(
        items=items,
        total_items=total_count,
        page=page,
        limit=limit,
        base_url=base_url,
    )


@router.get("/rates/employee/{employee_id}", response_model=RateListResponse)
async def get_rates_by_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    read_model = RateReadModel(db)
    handler = GetRatesByEmployeeHandler(read_model)

    query = GetRatesByEmployeeQuery(employee_id=employee_id)
    rates = await handler.handle(query)

    return RateListResponse(items=rates, total=len(rates))


@router.get("/rates/employee/{employee_id}/active", response_model=RateView)
async def get_active_rate(
    employee_id: UUID, check_date: date = date.today(), db: AsyncSession = Depends(get_db)
):
    read_model = RateReadModel(db)
    handler = GetActiveRateHandler(read_model)

    query = GetActiveRateQuery(employee_id=employee_id, check_date=check_date)
    rate = await handler.handle(query)

    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active rate found")

    return rate


@router.post("/bonuses/", response_model=BonusView, status_code=status.HTTP_201_CREATED)
async def create_bonus(request: CreateBonusRequest, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyBonusRepository(db)
    handler = CreateBonusHandler(repository)

    command = CreateBonusCommand(
        employee_id=request.employee_id,
        bonus_type=request.bonus_type,
        amount=request.amount,
        currency=request.currency,
        payment_date=request.payment_date,
        description=request.description,
    )

    try:
        bonus = await handler.handle(command)
        await db.commit()
        # Fetch from ReadModel after write
        read_model = BonusReadModel(db)
        view = await read_model.get_by_id(bonus.id)
        return view
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/bonuses/{bonus_id}", response_model=BonusView)
async def get_bonus(bonus_id: UUID, db: AsyncSession = Depends(get_db)):
    read_model = BonusReadModel(db)
    handler = GetBonusHandler(read_model)

    query = GetBonusQuery(bonus_id=bonus_id)
    bonus = await handler.handle(query)

    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bonus not found")

    return bonus


@router.get("/bonuses/", response_model=PaginatedResponse[BonusView])
async def list_bonuses(
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

    read_model = BonusReadModel(db)
    handler = ListBonusesHandler(read_model)

    query = ListBonusesQuery(skip=skip, limit=limit)
    items, total_count = await handler.handle(query)

    base_url = str(request.url).split("?")[0]
    return create_paginated_response(
        items=items,
        total_items=total_count,
        page=page,
        limit=limit,
        base_url=base_url,
    )


@router.get("/bonuses/employee/{employee_id}", response_model=BonusListResponse)
async def get_bonuses_by_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    read_model = BonusReadModel(db)
    handler = GetBonusesByEmployeeHandler(read_model)

    query = GetBonusesByEmployeeQuery(employee_id=employee_id)
    bonuses = await handler.handle(query)

    return BonusListResponse(items=bonuses, total=len(bonuses))
