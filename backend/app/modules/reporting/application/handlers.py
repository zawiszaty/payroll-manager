from datetime import date
from pathlib import Path
from typing import Any

from app.modules.reporting.application.commands import (
    CreateReportCommand,
    DeleteReportCommand,
    GenerateReportCommand,
)
from app.modules.reporting.application.queries import (
    GetReportQuery,
    ListReportsByStatusQuery,
    ListReportsByTypeQuery,
    ListReportsQuery,
)
from app.modules.reporting.domain.entities import Report
from app.modules.reporting.domain.repository import ReportRepository
from app.modules.reporting.domain.services import (
    CreateReportService,
)
from app.modules.reporting.domain.value_objects import (
    ReportFormat,
    ReportParameters,
    ReportStatus,
    ReportType,
)
from app.modules.reporting.infrastructure.adapters import ReportingDataAdapter
from app.modules.reporting.infrastructure.generators import ReportGeneratorFactory


class CreateReportHandler:
    def __init__(self, repository: ReportRepository):
        self.repository = repository
        self.service = CreateReportService(repository)

    async def handle(self, command: CreateReportCommand) -> Report:
        report_type = ReportType(command.report_type)
        report_format = ReportFormat(command.format)

        # Convert string dates to date objects
        start_date = None
        end_date = None

        if command.start_date:
            try:
                start_date = date.fromisoformat(command.start_date)
            except ValueError as e:
                raise ValueError(f"Invalid start_date format: {e}")

        if command.end_date:
            try:
                end_date = date.fromisoformat(command.end_date)
            except ValueError as e:
                raise ValueError(f"Invalid end_date format: {e}")

        parameters = ReportParameters(
            employee_id=command.employee_id,
            department=command.department,
            start_date=start_date,
            end_date=end_date,
            additional_filters=command.additional_filters,
        )

        return await self.service.create(
            name=command.name,
            report_type=report_type,
            format=report_format,
            parameters=parameters,
        )


class DeleteReportHandler:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    async def handle(self, command: DeleteReportCommand) -> None:
        report = await self.repository.get_by_id(command.report_id)
        if not report:
            raise ValueError(f"Report {command.report_id} not found")

        await self.repository.delete(command.report_id)


class GetReportHandler:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    async def handle(self, query: GetReportQuery) -> Report | None:
        return await self.repository.get_by_id(query.report_id)


class ListReportsHandler:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    async def handle(self, query: ListReportsQuery) -> list[Report]:
        return await self.repository.list_all()


class ListReportsByTypeHandler:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    async def handle(self, query: ListReportsByTypeQuery) -> list[Report]:
        report_type = ReportType(query.report_type)
        return await self.repository.list_by_type(report_type)


class ListReportsByStatusHandler:
    def __init__(self, repository: ReportRepository):
        self.repository = repository

    async def handle(self, query: ListReportsByStatusQuery) -> list[Report]:
        status = ReportStatus(query.status)
        return await self.repository.list_by_status(status)


class GenerateReportHandler:
    """
    Handler for GenerateReportCommand
    Orchestrates report generation using domain services and adapters
    """

    def __init__(
        self,
        repository: ReportRepository,
        generator_factory: ReportGeneratorFactory,
        data_adapter: ReportingDataAdapter,
    ):
        self.repository = repository
        self.generator_factory = generator_factory
        self.data_adapter = data_adapter

    async def handle(self, command: GenerateReportCommand) -> Report:
        """
        Handle report generation command
        Returns the updated report entity after generation
        """
        # Get the report
        report = await self.repository.get_by_id(command.report_id)
        if not report:
            raise ValueError(f"Report {command.report_id} not found")

        # Check if already completed
        if report.is_completed():
            raise ValueError("Report already generated")

        if report.is_processing():
            raise ValueError("Report is currently being generated")

        # Generate the report file
        await self._generate_report_file(report)

        return report

    async def _generate_report_file(self, report: Report) -> Path:
        report.start_processing()
        await self.repository.save(report)

        try:
            data = await self._fetch_report_data(report)
            generator = self.generator_factory.get_generator(report.format.value)
            file_path = await generator.generate(report, data)

            report.complete(str(file_path))
            await self.repository.save(report)

            return file_path

        except Exception as e:
            report.fail(str(e))
            await self.repository.save(report)
            raise

    async def _fetch_report_data(self, report: Report) -> dict[str, Any]:
        if report.report_type == ReportType.PAYROLL_SUMMARY:
            return await self._fetch_payroll_summary_data(report)
        elif report.report_type == ReportType.EMPLOYEE_COMPENSATION:
            return await self._fetch_employee_compensation_data(report)
        elif report.report_type == ReportType.ABSENCE_SUMMARY:
            return await self._fetch_absence_summary_data(report)
        elif report.report_type == ReportType.TIMESHEET_SUMMARY:
            return await self._fetch_timesheet_summary_data(report)
        elif report.report_type == ReportType.TAX_REPORT:
            return await self._fetch_tax_report_data(report)
        else:
            return await self._fetch_custom_report_data(report)

    async def _fetch_payroll_summary_data(self, report: Report) -> dict[str, Any]:
        return await self.data_adapter.fetch_payroll_summary_data(report.parameters)

    async def _fetch_employee_compensation_data(self, report: Report) -> dict[str, Any]:
        return await self.data_adapter.fetch_employee_compensation_data(report.parameters)

    async def _fetch_absence_summary_data(self, report: Report) -> dict[str, Any]:
        return await self.data_adapter.fetch_absence_summary_data(report.parameters)

    async def _fetch_timesheet_summary_data(self, report: Report) -> dict[str, Any]:
        return await self.data_adapter.fetch_timesheet_summary_data(report.parameters)

    async def _fetch_tax_report_data(self, report: Report) -> dict[str, Any]:
        return await self.data_adapter.fetch_tax_report_data(report.parameters)

    async def _fetch_custom_report_data(self, report: Report) -> dict[str, Any]:
        return await self.data_adapter.fetch_custom_report_data(report.parameters)
