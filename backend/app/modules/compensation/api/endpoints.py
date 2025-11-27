from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.compensation.domain.value_objects import RateType, BonusType
from app.modules.compensation.infrastructure.repository import (
    SQLAlchemyRateRepository,
    SQLAlchemyBonusRepository,
)
from app.modules.compensation.application.commands import CreateRateCommand, CreateBonusCommand
from app.modules.compensation.application.queries import (
    GetRateQuery,
    GetRatesByEmployeeQuery,
    GetActiveRateQuery,
    ListRatesQuery,
    GetBonusQuery,
    GetBonusesByEmployeeQuery,
    ListBonusesQuery,
)
from app.modules.compensation.application.handlers import (
    CreateRateHandler,
    GetRateHandler,
    GetRatesByEmployeeHandler,
    GetActiveRateHandler,
    ListRatesHandler,
    CreateBonusHandler,
    GetBonusHandler,
    GetBonusesByEmployeeHandler,
    ListBonusesHandler,
)

router = APIRouter()


class RateResponse(BaseModel):
    id: UUID
    employee_id: UUID
    rate_type: RateType
    amount: Decimal
    currency: str
    valid_from: date
    valid_to: date | None
    description: str | None


class CreateRateRequest(BaseModel):
    employee_id: UUID
    rate_type: RateType
    amount: Decimal
    currency: str = "USD"
    valid_from: date
    valid_to: date | None = None
    description: str | None = None


class BonusResponse(BaseModel):
    id: UUID
    employee_id: UUID
    bonus_type: BonusType
    amount: Decimal
    currency: str
    payment_date: date
    description: str | None


class CreateBonusRequest(BaseModel):
    employee_id: UUID
    bonus_type: BonusType
    amount: Decimal
    currency: str = "USD"
    payment_date: date
    description: str | None = None


def rate_to_response(rate) -> RateResponse:
    return RateResponse(
        id=rate.id,
        employee_id=rate.employee_id,
        rate_type=rate.rate_type,
        amount=rate.amount.amount,
        currency=rate.amount.currency,
        valid_from=rate.date_range.valid_from,
        valid_to=rate.date_range.valid_to,
        description=rate.description,
    )


def bonus_to_response(bonus) -> BonusResponse:
    return BonusResponse(
        id=bonus.id,
        employee_id=bonus.employee_id,
        bonus_type=bonus.bonus_type,
        amount=bonus.amount.amount,
        currency=bonus.amount.currency,
        payment_date=bonus.payment_date,
        description=bonus.description,
    )


@router.post("/rates/", response_model=RateResponse, status_code=status.HTTP_201_CREATED)
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
        return rate_to_response(rate)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/rates/{rate_id}", response_model=RateResponse)
async def get_rate(rate_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyRateRepository(db)
    handler = GetRateHandler(repository)

    query = GetRateQuery(rate_id=rate_id)
    rate = await handler.handle(query)

    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rate not found")

    return rate_to_response(rate)


@router.get("/rates/", response_model=List[RateResponse])
async def list_rates(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyRateRepository(db)
    handler = ListRatesHandler(repository)

    query = ListRatesQuery(skip=skip, limit=limit)
    rates = await handler.handle(query)

    return [rate_to_response(rate) for rate in rates]


@router.get("/rates/employee/{employee_id}", response_model=List[RateResponse])
async def get_rates_by_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyRateRepository(db)
    handler = GetRatesByEmployeeHandler(repository)

    query = GetRatesByEmployeeQuery(employee_id=employee_id)
    rates = await handler.handle(query)

    return [rate_to_response(rate) for rate in rates]


@router.get("/rates/employee/{employee_id}/active", response_model=RateResponse)
async def get_active_rate(employee_id: UUID, check_date: date = date.today(), db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyRateRepository(db)
    handler = GetActiveRateHandler(repository)

    query = GetActiveRateQuery(employee_id=employee_id, check_date=check_date)
    rate = await handler.handle(query)

    if not rate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active rate found")

    return rate_to_response(rate)


@router.post("/bonuses/", response_model=BonusResponse, status_code=status.HTTP_201_CREATED)
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
        return bonus_to_response(bonus)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/bonuses/{bonus_id}", response_model=BonusResponse)
async def get_bonus(bonus_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyBonusRepository(db)
    handler = GetBonusHandler(repository)

    query = GetBonusQuery(bonus_id=bonus_id)
    bonus = await handler.handle(query)

    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bonus not found")

    return bonus_to_response(bonus)


@router.get("/bonuses/", response_model=List[BonusResponse])
async def list_bonuses(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyBonusRepository(db)
    handler = ListBonusesHandler(repository)

    query = ListBonusesQuery(skip=skip, limit=limit)
    bonuses = await handler.handle(query)

    return [bonus_to_response(bonus) for bonus in bonuses]


@router.get("/bonuses/employee/{employee_id}", response_model=List[BonusResponse])
async def get_bonuses_by_employee(employee_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyBonusRepository(db)
    handler = GetBonusesByEmployeeHandler(repository)

    query = GetBonusesByEmployeeQuery(employee_id=employee_id)
    bonuses = await handler.handle(query)

    return [bonus_to_response(bonus) for bonus in bonuses]
