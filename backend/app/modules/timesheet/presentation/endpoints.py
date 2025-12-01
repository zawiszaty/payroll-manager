from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.timesheet.application.commands import (
    ApproveTimesheetCommand,
    CreateTimesheetCommand,
    DeleteTimesheetCommand,
    RejectTimesheetCommand,
    SubmitTimesheetCommand,
    UpdateTimesheetCommand,
)
from app.modules.timesheet.application.handlers import (
    ApproveTimesheetHandler,
    CreateTimesheetHandler,
    DeleteTimesheetHandler,
    GetPendingApprovalHandler,
    GetTimesheetHandler,
    GetTimesheetsByEmployeeAndDateRangeHandler,
    GetTimesheetsByEmployeeHandler,
    GetTimesheetsByStatusHandler,
    ListTimesheetsHandler,
    RejectTimesheetHandler,
    SubmitTimesheetHandler,
    SumHoursInIntervalHandler,
    UpdateTimesheetHandler,
)
from app.modules.timesheet.application.queries import (
    GetPendingApprovalQuery,
    GetTimesheetQuery,
    GetTimesheetsByEmployeeAndDateRangeQuery,
    GetTimesheetsByEmployeeQuery,
    GetTimesheetsByStatusQuery,
    ListTimesheetsQuery,
    SumHoursInIntervalQuery,
)
from app.modules.timesheet.infrastructure.repository import (
    SQLAlchemyTimesheetRepository,
)
from app.modules.timesheet.presentation.views import (
    ApproveTimesheetRequest,
    CreateTimesheetRequest,
    HoursSummaryResponse,
    RejectTimesheetRequest,
    TimesheetResponse,
    UpdateTimesheetRequest,
)

router = APIRouter()


@router.post("/", response_model=TimesheetResponse, status_code=status.HTTP_201_CREATED)
async def create_timesheet(
    request: CreateTimesheetRequest, db: AsyncSession = Depends(get_db)
) -> TimesheetResponse:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = CreateTimesheetHandler(repository)

    command = CreateTimesheetCommand(
        employee_id=request.employee_id,
        work_date=request.work_date,
        hours=request.hours,
        overtime_hours=request.overtime_hours,
        overtime_type=request.overtime_type,
        project_id=request.project_id,
        task_description=request.task_description,
    )

    try:
        timesheet = await handler.handle(command)
        await db.commit()
        return TimesheetResponse.from_entity(timesheet)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{timesheet_id}", response_model=TimesheetResponse)
async def get_timesheet(
    timesheet_id: UUID, db: AsyncSession = Depends(get_db)
) -> TimesheetResponse:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = GetTimesheetHandler(repository)

    query = GetTimesheetQuery(timesheet_id=timesheet_id)
    timesheet = await handler.handle(query)

    if not timesheet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timesheet not found")

    return TimesheetResponse.from_entity(timesheet)


@router.get("/", response_model=list[TimesheetResponse])
async def list_timesheets(db: AsyncSession = Depends(get_db)) -> list[TimesheetResponse]:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = ListTimesheetsHandler(repository)

    query = ListTimesheetsQuery()
    timesheets = await handler.handle(query)

    return [TimesheetResponse.from_entity(ts) for ts in timesheets]


@router.get("/employee/{employee_id}", response_model=list[TimesheetResponse])
async def get_timesheets_by_employee(
    employee_id: UUID, db: AsyncSession = Depends(get_db)
) -> list[TimesheetResponse]:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = GetTimesheetsByEmployeeHandler(repository)

    query = GetTimesheetsByEmployeeQuery(employee_id=employee_id)
    timesheets = await handler.handle(query)

    return [TimesheetResponse.from_entity(ts) for ts in timesheets]


@router.get("/employee/{employee_id}/period", response_model=list[TimesheetResponse])
async def get_timesheets_by_employee_and_date_range(
    employee_id: UUID,
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
) -> list[TimesheetResponse]:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = GetTimesheetsByEmployeeAndDateRangeHandler(repository)

    query = GetTimesheetsByEmployeeAndDateRangeQuery(
        employee_id=employee_id, start_date=start_date, end_date=end_date
    )
    timesheets = await handler.handle(query)

    return [TimesheetResponse.from_entity(ts) for ts in timesheets]


@router.get("/status/{status_value}", response_model=list[TimesheetResponse])
async def get_timesheets_by_status(
    status_value: str, db: AsyncSession = Depends(get_db)
) -> list[TimesheetResponse]:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = GetTimesheetsByStatusHandler(repository)

    query = GetTimesheetsByStatusQuery(status=status_value)
    timesheets = await handler.handle(query)

    return [TimesheetResponse.from_entity(ts) for ts in timesheets]


@router.get("/pending-approval/list", response_model=list[TimesheetResponse])
async def get_pending_approval(db: AsyncSession = Depends(get_db)) -> list[TimesheetResponse]:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = GetPendingApprovalHandler(repository)

    query = GetPendingApprovalQuery()
    timesheets = await handler.handle(query)

    return [TimesheetResponse.from_entity(ts) for ts in timesheets]


@router.get("/employee/{employee_id}/hours-summary", response_model=HoursSummaryResponse)
async def sum_hours_in_interval(
    employee_id: UUID,
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
) -> HoursSummaryResponse:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = SumHoursInIntervalHandler(repository)

    query = SumHoursInIntervalQuery(
        employee_id=employee_id, start_date=start_date, end_date=end_date
    )
    total_hours = await handler.handle(query)

    return HoursSummaryResponse(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        total_hours=total_hours,
    )


@router.put("/{timesheet_id}", response_model=TimesheetResponse)
async def update_timesheet(
    timesheet_id: UUID,
    request: UpdateTimesheetRequest,
    db: AsyncSession = Depends(get_db),
) -> TimesheetResponse:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = UpdateTimesheetHandler(repository)

    command = UpdateTimesheetCommand(
        timesheet_id=timesheet_id,
        hours=request.hours,
        overtime_hours=request.overtime_hours,
        overtime_type=request.overtime_type,
        project_id=request.project_id,
        task_description=request.task_description,
    )

    try:
        timesheet = await handler.handle(command)
        await db.commit()
        return TimesheetResponse.from_entity(timesheet)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{timesheet_id}/submit", response_model=TimesheetResponse)
async def submit_timesheet(
    timesheet_id: UUID, db: AsyncSession = Depends(get_db)
) -> TimesheetResponse:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = SubmitTimesheetHandler(repository)

    command = SubmitTimesheetCommand(timesheet_id=timesheet_id)

    try:
        timesheet = await handler.handle(command)
        await db.commit()
        return TimesheetResponse.from_entity(timesheet)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{timesheet_id}/approve", response_model=TimesheetResponse)
async def approve_timesheet(
    timesheet_id: UUID,
    request: ApproveTimesheetRequest,
    db: AsyncSession = Depends(get_db),
) -> TimesheetResponse:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = ApproveTimesheetHandler(repository)

    command = ApproveTimesheetCommand(timesheet_id=timesheet_id, approved_by=request.approved_by)

    try:
        timesheet = await handler.handle(command)
        await db.commit()
        return TimesheetResponse.from_entity(timesheet)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{timesheet_id}/reject", response_model=TimesheetResponse)
async def reject_timesheet(
    timesheet_id: UUID,
    request: RejectTimesheetRequest,
    db: AsyncSession = Depends(get_db),
) -> TimesheetResponse:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = RejectTimesheetHandler(repository)

    command = RejectTimesheetCommand(timesheet_id=timesheet_id, reason=request.reason)

    try:
        timesheet = await handler.handle(command)
        await db.commit()
        return TimesheetResponse.from_entity(timesheet)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{timesheet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_timesheet(timesheet_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    repository = SQLAlchemyTimesheetRepository(db)
    handler = DeleteTimesheetHandler(repository)

    command = DeleteTimesheetCommand(timesheet_id=timesheet_id)

    try:
        await handler.handle(command)
        await db.commit()
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
