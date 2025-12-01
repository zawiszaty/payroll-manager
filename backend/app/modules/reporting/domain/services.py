from app.modules.reporting.domain.entities import Report
from app.modules.reporting.domain.repository import ReportRepository
from app.modules.reporting.domain.value_objects import (
    ReportFormat,
    ReportParameters,
    ReportType,
)


class CreateReportService:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    async def create(
        self,
        name: str,
        report_type: ReportType,
        format: ReportFormat,
        parameters: ReportParameters,
    ) -> Report:
        report = Report(
            name=name,
            report_type=report_type,
            format=format,
            parameters=parameters,
        )
        return await self.repository.save(report)


class ProcessReportService:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    async def start_processing(self, report: Report) -> Report:
        report.start_processing()
        return await self.repository.update(report)

    async def complete_processing(self, report: Report, file_path: str) -> Report:
        report.complete(file_path)
        return await self.repository.update(report)

    async def fail_processing(self, report: Report, error_message: str) -> Report:
        report.fail(error_message)
        return await self.repository.update(report)
