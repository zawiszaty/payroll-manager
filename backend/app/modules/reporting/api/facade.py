from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.modules.reporting.domain.repository import ReportRepository


@dataclass
class ReportDTO:
    id: UUID
    name: str
    report_type: str
    format: str
    status: str
    file_path: str | None
    created_at: datetime
    completed_at: datetime | None


class IReportingFacade(ABC):
    @abstractmethod
    async def get_report(self, report_id: UUID) -> ReportDTO | None:
        pass

    @abstractmethod
    async def list_reports_by_type(self, report_type: str) -> list[ReportDTO]:
        pass

    @abstractmethod
    async def list_reports_by_status(self, status: str) -> list[ReportDTO]:
        pass

    @abstractmethod
    async def report_exists(self, report_id: UUID) -> bool:
        pass


class ReportingFacade(IReportingFacade):
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    async def get_report(self, report_id: UUID) -> ReportDTO | None:
        report = await self.repository.get_by_id(report_id)
        if not report:
            return None

        return ReportDTO(
            id=report.id,
            name=report.name,
            report_type=report.report_type.value,
            format=report.format.value,
            status=report.status.value,
            file_path=report.file_path,
            created_at=report.created_at,
            completed_at=report.completed_at,
        )

    async def list_reports_by_type(self, report_type: str) -> list[ReportDTO]:
        from app.modules.reporting.domain.value_objects import ReportType

        reports = await self.repository.list_by_type(ReportType(report_type))
        return [
            ReportDTO(
                id=report.id,
                name=report.name,
                report_type=report.report_type.value,
                format=report.format.value,
                status=report.status.value,
                file_path=report.file_path,
                created_at=report.created_at,
                completed_at=report.completed_at,
            )
            for report in reports
        ]

    async def list_reports_by_status(self, status: str) -> list[ReportDTO]:
        from app.modules.reporting.domain.value_objects import ReportStatus

        reports = await self.repository.list_by_status(ReportStatus(status))
        return [
            ReportDTO(
                id=report.id,
                name=report.name,
                report_type=report.report_type.value,
                format=report.format.value,
                status=report.status.value,
                file_path=report.file_path,
                created_at=report.created_at,
                completed_at=report.completed_at,
            )
            for report in reports
        ]

    async def report_exists(self, report_id: UUID) -> bool:
        report = await self.repository.get_by_id(report_id)
        return report is not None
