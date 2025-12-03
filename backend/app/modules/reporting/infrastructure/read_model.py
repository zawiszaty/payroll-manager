from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reporting.domain.value_objects import ReportStatus, ReportType
from app.modules.reporting.infrastructure.models import ReportORM
from app.modules.reporting.presentation.schemas import ReportResponse


class ReportReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, report_id: UUID) -> Optional[ReportResponse]:
        stmt = select(ReportORM).where(ReportORM.id == report_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return ReportResponse(
            id=orm.id,
            name=orm.name,
            report_type=orm.report_type.value,
            format=orm.format.value,
            status=orm.status.value,
            parameters=orm.parameters or {},
            file_path=orm.file_path,
            error_message=orm.error_message,
            created_at=orm.created_at,
            completed_at=orm.completed_at,
        )

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list[ReportResponse], int]:
        count_stmt = select(func.count()).select_from(ReportORM)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        stmt = select(ReportORM).offset(skip).limit(limit).order_by(ReportORM.created_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            ReportResponse(
                id=orm.id,
                name=orm.name,
                report_type=orm.report_type.value,
                format=orm.format.value,
                status=orm.status.value,
                parameters=orm.parameters or {},
                file_path=orm.file_path,
                error_message=orm.error_message,
                created_at=orm.created_at,
                completed_at=orm.completed_at,
            )
            for orm in orms
        ]

        return items, total_count

    async def get_by_type(
        self, report_type: ReportType, skip: int = 0, limit: int = 100
    ) -> tuple[list[ReportResponse], int]:
        count_stmt = (
            select(func.count()).select_from(ReportORM).where(ReportORM.report_type == report_type)
        )
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        stmt = (
            select(ReportORM)
            .where(ReportORM.report_type == report_type)
            .offset(skip)
            .limit(limit)
            .order_by(ReportORM.created_at.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            ReportResponse(
                id=orm.id,
                name=orm.name,
                report_type=orm.report_type.value,
                format=orm.format.value,
                status=orm.status.value,
                parameters=orm.parameters or {},
                file_path=orm.file_path,
                error_message=orm.error_message,
                created_at=orm.created_at,
                completed_at=orm.completed_at,
            )
            for orm in orms
        ]

        return items, total_count

    async def get_by_status(
        self, status: ReportStatus, skip: int = 0, limit: int = 100
    ) -> tuple[list[ReportResponse], int]:
        count_stmt = select(func.count()).select_from(ReportORM).where(ReportORM.status == status)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        stmt = (
            select(ReportORM)
            .where(ReportORM.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(ReportORM.created_at.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            ReportResponse(
                id=orm.id,
                name=orm.name,
                report_type=orm.report_type.value,
                format=orm.format.value,
                status=orm.status.value,
                parameters=orm.parameters or {},
                file_path=orm.file_path,
                error_message=orm.error_message,
                created_at=orm.created_at,
                completed_at=orm.completed_at,
            )
            for orm in orms
        ]

        return items, total_count
