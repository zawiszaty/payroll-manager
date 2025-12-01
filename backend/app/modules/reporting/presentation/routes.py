from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.reporting.application.commands import (
    CreateReportCommand,
    DeleteReportCommand,
    GenerateReportCommand,
)
from app.modules.reporting.application.handlers import (
    CreateReportHandler,
    DeleteReportHandler,
    GenerateReportHandler,
    GetReportHandler,
    ListReportsByStatusHandler,
    ListReportsByTypeHandler,
    ListReportsHandler,
)
from app.modules.reporting.application.queries import (
    GetReportQuery,
    ListReportsByStatusQuery,
    ListReportsByTypeQuery,
    ListReportsQuery,
)
from app.modules.reporting.infrastructure.adapters import ReportingDataAdapter
from app.modules.reporting.infrastructure.generators import ReportGeneratorFactory
from app.modules.reporting.infrastructure.repository import (
    SQLAlchemyReportRepository,
)
from app.modules.reporting.presentation.schemas import (
    CreateReportRequest,
    ReportListResponse,
    ReportResponse,
)

router = APIRouter()


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    request: CreateReportRequest, db: AsyncSession = Depends(get_db)
) -> ReportResponse:
    repository = SQLAlchemyReportRepository(db)
    handler = CreateReportHandler(repository)

    command = CreateReportCommand(
        name=request.name,
        report_type=request.report_type,
        format=request.format,
        employee_id=request.employee_id,
        department=request.department,
        start_date=request.start_date,
        end_date=request.end_date,
        additional_filters=request.additional_filters,
    )

    try:
        report = await handler.handle(command)
        await db.commit()
        return ReportResponse.from_entity(report)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: UUID, db: AsyncSession = Depends(get_db)) -> ReportResponse:
    repository = SQLAlchemyReportRepository(db)
    handler = GetReportHandler(repository)

    query = GetReportQuery(report_id=report_id)
    report = await handler.handle(query)

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    return ReportResponse.from_entity(report)


@router.get("/", response_model=ReportListResponse)
async def list_reports(db: AsyncSession = Depends(get_db)) -> ReportListResponse:
    repository = SQLAlchemyReportRepository(db)
    handler = ListReportsHandler(repository)

    query = ListReportsQuery()
    reports = await handler.handle(query)

    return ReportListResponse(reports=[ReportResponse.from_entity(report) for report in reports])


@router.get("/type/{report_type}", response_model=ReportListResponse)
async def list_reports_by_type(
    report_type: str, db: AsyncSession = Depends(get_db)
) -> ReportListResponse:
    repository = SQLAlchemyReportRepository(db)
    handler = ListReportsByTypeHandler(repository)

    try:
        query = ListReportsByTypeQuery(report_type=report_type)
        reports = await handler.handle(query)
        return ReportListResponse(
            reports=[ReportResponse.from_entity(report) for report in reports]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/status/{status}", response_model=ReportListResponse)
async def list_reports_by_status(
    status: str, db: AsyncSession = Depends(get_db)
) -> ReportListResponse:
    repository = SQLAlchemyReportRepository(db)
    handler = ListReportsByStatusHandler(repository)

    try:
        query = ListReportsByStatusQuery(status=status)
        reports = await handler.handle(query)
        return ReportListResponse(
            reports=[ReportResponse.from_entity(report) for report in reports]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{report_id}/generate", response_model=ReportResponse)
async def generate_report(report_id: UUID, db: AsyncSession = Depends(get_db)) -> ReportResponse:
    repository = SQLAlchemyReportRepository(db)
    generator_factory = ReportGeneratorFactory()
    data_adapter = ReportingDataAdapter(db)
    handler = GenerateReportHandler(repository, generator_factory, data_adapter)

    command = GenerateReportCommand(report_id=report_id)

    try:
        report = await handler.handle(command)
        await db.commit()
        return ReportResponse.from_entity(report)
    except ValueError as e:
        await db.rollback()
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        elif "already generated" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report already generated. Use /download to get the file.",
            )
        elif "currently being generated" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Report is currently being generated. Please wait.",
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        )


@router.get("/{report_id}/download")
async def download_report(report_id: UUID, db: AsyncSession = Depends(get_db)):
    repository = SQLAlchemyReportRepository(db)
    handler = GetReportHandler(repository)

    query = GetReportQuery(report_id=report_id)
    report = await handler.handle(query)

    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    if not report.is_completed():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report is not ready for download. Current status: {report.status.value}. Please call /generate first.",
        )

    if not report.file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found")

    file_path = Path(report.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file does not exist on disk",
        )

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream",
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(report_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    repository = SQLAlchemyReportRepository(db)
    handler = DeleteReportHandler(repository)

    command = DeleteReportCommand(report_id=report_id)

    try:
        await handler.handle(command)
        await db.commit()
    except ValueError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
