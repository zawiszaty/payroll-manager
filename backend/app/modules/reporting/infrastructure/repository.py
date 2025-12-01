from datetime import date
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reporting.domain.entities import Report
from app.modules.reporting.domain.repository import ReportRepository
from app.modules.reporting.domain.value_objects import (
    ReportParameters,
    ReportStatus,
    ReportType,
)
from app.modules.reporting.infrastructure.models import ReportORM


class SQLAlchemyReportRepository(ReportRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        from app.shared.domain.events import get_event_dispatcher

        self.event_dispatcher = get_event_dispatcher()

    def _to_domain(self, orm: ReportORM) -> Report:
        params_dict = orm.parameters or {}

        # Parse ISO date strings back to date objects
        start_date = None
        end_date = None
        if params_dict.get("start_date"):
            start_date = date.fromisoformat(params_dict["start_date"])
        if params_dict.get("end_date"):
            end_date = date.fromisoformat(params_dict["end_date"])

        parameters = ReportParameters(
            employee_id=params_dict.get("employee_id"),
            department=params_dict.get("department"),
            start_date=start_date,
            end_date=end_date,
            additional_filters=params_dict.get("additional_filters"),
        )

        return Report(
            id=orm.id,
            name=orm.name,
            report_type=orm.report_type,
            format=orm.format,
            status=orm.status,
            parameters=parameters,
            file_path=orm.file_path,
            error_message=orm.error_message,
            created_at=orm.created_at,
            completed_at=orm.completed_at,
        )

    def _to_orm(self, report: Report) -> ReportORM:
        # Serialize date objects to ISO format strings for JSON storage
        params_dict = {
            "employee_id": report.parameters.employee_id,
            "department": report.parameters.department,
            "start_date": report.parameters.start_date.isoformat()
            if report.parameters.start_date
            else None,
            "end_date": report.parameters.end_date.isoformat()
            if report.parameters.end_date
            else None,
            "additional_filters": report.parameters.additional_filters,
        }

        return ReportORM(
            id=report.id,
            name=report.name,
            report_type=report.report_type,
            format=report.format,
            status=report.status,
            parameters=params_dict,
            file_path=report.file_path,
            error_message=report.error_message,
            created_at=report.created_at,
            completed_at=report.completed_at,
        )

    async def _dispatch_events(self, report: Report) -> None:
        import asyncio

        events = report.get_domain_events()
        for event in events:
            asyncio.create_task(self.event_dispatcher.dispatch(event))
        report.clear_domain_events()

    async def save(self, report: Report) -> Report:
        orm = self._to_orm(report)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        result = self._to_domain(orm)
        await self._dispatch_events(report)
        return result

    async def get_by_id(self, report_id: UUID) -> Report | None:
        result = await self.session.execute(select(ReportORM).where(ReportORM.id == report_id))
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_all(self) -> list[Report]:
        result = await self.session.execute(select(ReportORM).order_by(ReportORM.created_at.desc()))
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def list_by_type(self, report_type: ReportType) -> list[Report]:
        result = await self.session.execute(
            select(ReportORM)
            .where(ReportORM.report_type == report_type)
            .order_by(ReportORM.created_at.desc())
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def list_by_status(self, status: ReportStatus) -> list[Report]:
        result = await self.session.execute(
            select(ReportORM)
            .where(ReportORM.status == status)
            .order_by(ReportORM.created_at.desc())
        )
        return [self._to_domain(orm) for orm in result.scalars().all()]

    async def update(self, report: Report) -> Report:
        result = await self.session.execute(select(ReportORM).where(ReportORM.id == report.id))
        orm = result.scalar_one_or_none()
        if not orm:
            raise ValueError(f"Report {report.id} not found")

        orm.name = report.name
        orm.report_type = report.report_type
        orm.format = report.format
        orm.status = report.status
        orm.parameters = {
            "employee_id": report.parameters.employee_id,
            "department": report.parameters.department,
            "start_date": report.parameters.start_date.isoformat()
            if report.parameters.start_date
            else None,
            "end_date": report.parameters.end_date.isoformat()
            if report.parameters.end_date
            else None,
            "additional_filters": report.parameters.additional_filters,
        }
        orm.file_path = report.file_path
        orm.error_message = report.error_message
        orm.completed_at = report.completed_at

        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def delete(self, report_id: UUID) -> None:
        await self.session.execute(delete(ReportORM).where(ReportORM.id == report_id))
        await self.session.flush()
