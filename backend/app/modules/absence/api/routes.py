from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.absence.api.schemas import (
    AbsenceBalanceCreate,
    AbsenceBalanceDetailResponse,
    AbsenceBalanceListResponse,
    AbsenceBalanceResponse,
    AbsenceBalanceUpdate,
    AbsenceCreate,
    AbsenceListResponse,
    AbsenceResponse,
)
from app.modules.absence.application.commands import (
    ApproveAbsenceCommand,
    CancelAbsenceCommand,
    CreateAbsenceBalanceCommand,
    CreateAbsenceCommand,
    RejectAbsenceCommand,
    UpdateAbsenceBalanceCommand,
)
from app.modules.absence.application.handlers import (
    ApproveAbsenceHandler,
    CancelAbsenceHandler,
    CreateAbsenceBalanceHandler,
    CreateAbsenceHandler,
    GetAbsenceBalanceHandler,
    GetAbsenceBalancesByEmployeeAndYearHandler,
    GetAbsenceBalancesByEmployeeHandler,
    GetAbsenceHandler,
    GetAbsencesByEmployeeHandler,
    ListAbsenceBalancesHandler,
    ListAbsencesHandler,
    RejectAbsenceHandler,
    UpdateAbsenceBalanceHandler,
)
from app.modules.absence.application.queries import (
    GetAbsenceBalanceQuery,
    GetAbsenceBalancesByEmployeeAndYearQuery,
    GetAbsenceBalancesByEmployeeQuery,
    GetAbsenceQuery,
    GetAbsencesByEmployeeQuery,
    ListAbsenceBalancesQuery,
    ListAbsencesQuery,
)
from app.modules.absence.infrastructure.repository import (
    SQLAlchemyAbsenceBalanceRepository,
    SQLAlchemyAbsenceRepository,
)

router = APIRouter(tags=["absence"])


def _to_absence_response(absence) -> AbsenceResponse:
    return AbsenceResponse(
        id=absence.id,
        employee_id=absence.employee_id,
        absence_type=absence.absence_type,
        start_date=absence.period.start_date,
        end_date=absence.period.end_date,
        status=absence.status,
        reason=absence.reason,
        notes=absence.notes,
    )


def _to_balance_detail_response(balance) -> AbsenceBalanceDetailResponse:
    return AbsenceBalanceDetailResponse(
        id=balance.id,
        employee_id=balance.employee_id,
        absence_type=balance.absence_type,
        year=balance.year,
        total_days=balance.total_days,
        used_days=balance.used_days,
    )


def _to_balance_response(balance) -> AbsenceBalanceResponse:
    return AbsenceBalanceResponse(
        id=balance.id,
        employee_id=balance.employee_id,
        absence_type=balance.absence_type,
        year=balance.year,
        total_days=balance.total_days,
        used_days=balance.used_days,
        remaining_days=balance.remaining_days(),
    )


@router.post("/absences/", response_model=AbsenceResponse, status_code=201)
async def create_absence(data: AbsenceCreate, session: AsyncSession = Depends(get_db)):
    absence_repo = SQLAlchemyAbsenceRepository(session)
    balance_repo = SQLAlchemyAbsenceBalanceRepository(session)

    command = CreateAbsenceCommand(
        employee_id=data.employee_id,
        absence_type=data.absence_type,
        start_date=data.start_date,
        end_date=data.end_date,
        reason=data.reason,
        notes=data.notes,
    )

    handler = CreateAbsenceHandler(absence_repo, balance_repo)

    try:
        absence = await handler.handle(command)
        await session.commit()
        return _to_absence_response(absence)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/absences/{absence_id}", response_model=AbsenceResponse)
async def get_absence(absence_id: UUID, session: AsyncSession = Depends(get_db)):
    absence_repo = SQLAlchemyAbsenceRepository(session)
    handler = GetAbsenceHandler(absence_repo)

    try:
        absence = await handler.handle(GetAbsenceQuery(absence_id=absence_id))
        return _to_absence_response(absence)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/absences/", response_model=AbsenceListResponse)
async def list_absences(session: AsyncSession = Depends(get_db)):
    absence_repo = SQLAlchemyAbsenceRepository(session)
    handler = ListAbsencesHandler(absence_repo)
    absences = await handler.handle(ListAbsencesQuery())
    items = [_to_absence_response(absence) for absence in absences]
    return AbsenceListResponse(items=items, total=len(items))


@router.get("/absences/employee/{employee_id}", response_model=AbsenceListResponse)
async def get_absences_by_employee(employee_id: UUID, session: AsyncSession = Depends(get_db)):
    absence_repo = SQLAlchemyAbsenceRepository(session)
    handler = GetAbsencesByEmployeeHandler(absence_repo)
    absences = await handler.handle(GetAbsencesByEmployeeQuery(employee_id=employee_id))
    items = [_to_absence_response(absence) for absence in absences]
    return AbsenceListResponse(items=items, total=len(items))


@router.post("/absences/{absence_id}/approve", response_model=AbsenceResponse)
async def approve_absence(absence_id: UUID, session: AsyncSession = Depends(get_db)):
    absence_repo = SQLAlchemyAbsenceRepository(session)
    balance_repo = SQLAlchemyAbsenceBalanceRepository(session)

    handler = ApproveAbsenceHandler(absence_repo, balance_repo)
    command = ApproveAbsenceCommand(absence_id=absence_id)

    try:
        absence = await handler.handle(command)
        await session.commit()
        return _to_absence_response(absence)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/absences/{absence_id}/reject", response_model=AbsenceResponse)
async def reject_absence(absence_id: UUID, session: AsyncSession = Depends(get_db)):
    absence_repo = SQLAlchemyAbsenceRepository(session)
    handler = RejectAbsenceHandler(absence_repo)
    command = RejectAbsenceCommand(absence_id=absence_id)

    try:
        absence = await handler.handle(command)
        await session.commit()
        return _to_absence_response(absence)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/absences/{absence_id}/cancel", response_model=AbsenceResponse)
async def cancel_absence(absence_id: UUID, session: AsyncSession = Depends(get_db)):
    absence_repo = SQLAlchemyAbsenceRepository(session)
    balance_repo = SQLAlchemyAbsenceBalanceRepository(session)

    handler = CancelAbsenceHandler(absence_repo, balance_repo)
    command = CancelAbsenceCommand(absence_id=absence_id)

    try:
        absence = await handler.handle(command)
        await session.commit()
        return _to_absence_response(absence)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/balances/", response_model=AbsenceBalanceDetailResponse, status_code=201)
async def create_absence_balance(
    data: AbsenceBalanceCreate, session: AsyncSession = Depends(get_db)
):
    balance_repo = SQLAlchemyAbsenceBalanceRepository(session)

    command = CreateAbsenceBalanceCommand(
        employee_id=data.employee_id,
        absence_type=data.absence_type,
        year=data.year,
        total_days=data.total_days,
    )

    handler = CreateAbsenceBalanceHandler(balance_repo)

    try:
        balance = await handler.handle(command)
        await session.commit()
        return _to_balance_detail_response(balance)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/balances/{balance_id}", response_model=AbsenceBalanceResponse)
async def get_absence_balance(balance_id: UUID, session: AsyncSession = Depends(get_db)):
    balance_repo = SQLAlchemyAbsenceBalanceRepository(session)
    handler = GetAbsenceBalanceHandler(balance_repo)

    try:
        balance = await handler.handle(GetAbsenceBalanceQuery(balance_id=balance_id))
        return _to_balance_response(balance)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/balances/", response_model=AbsenceBalanceListResponse)
async def list_absence_balances(session: AsyncSession = Depends(get_db)):
    balance_repo = SQLAlchemyAbsenceBalanceRepository(session)
    handler = ListAbsenceBalancesHandler(balance_repo)
    balances = await handler.handle(ListAbsenceBalancesQuery())
    items = [_to_balance_response(balance) for balance in balances]
    return AbsenceBalanceListResponse(items=items, total=len(items))


@router.get("/balances/employee/{employee_id}", response_model=AbsenceBalanceListResponse)
async def get_absence_balances_by_employee(
    employee_id: UUID, session: AsyncSession = Depends(get_db)
):
    balance_repo = SQLAlchemyAbsenceBalanceRepository(session)
    handler = GetAbsenceBalancesByEmployeeHandler(balance_repo)
    balances = await handler.handle(GetAbsenceBalancesByEmployeeQuery(employee_id=employee_id))
    items = [_to_balance_response(balance) for balance in balances]
    return AbsenceBalanceListResponse(items=items, total=len(items))


@router.get(
    "/balances/employee/{employee_id}/year/{year}",
    response_model=AbsenceBalanceListResponse,
)
async def get_absence_balances_by_employee_and_year(
    employee_id: UUID, year: int, session: AsyncSession = Depends(get_db)
):
    balance_repo = SQLAlchemyAbsenceBalanceRepository(session)
    handler = GetAbsenceBalancesByEmployeeAndYearHandler(balance_repo)
    balances = await handler.handle(
        GetAbsenceBalancesByEmployeeAndYearQuery(employee_id=employee_id, year=year)
    )
    items = [_to_balance_response(balance) for balance in balances]
    return AbsenceBalanceListResponse(items=items, total=len(items))


@router.patch("/balances/{balance_id}", response_model=AbsenceBalanceDetailResponse)
async def update_absence_balance(
    balance_id: UUID, data: AbsenceBalanceUpdate, session: AsyncSession = Depends(get_db)
):
    balance_repo = SQLAlchemyAbsenceBalanceRepository(session)

    command = UpdateAbsenceBalanceCommand(balance_id=balance_id, total_days=data.total_days)

    handler = UpdateAbsenceBalanceHandler(balance_repo)

    try:
        balance = await handler.handle(command)
        await session.commit()
        return _to_balance_detail_response(balance)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
