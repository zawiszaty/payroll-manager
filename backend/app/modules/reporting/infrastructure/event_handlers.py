"""Event handlers for reporting module"""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database import AsyncSessionLocal
from app.modules.reporting.domain.value_objects import ReportType
from app.modules.reporting.infrastructure.adapters import ReportingDataAdapter
from app.modules.reporting.infrastructure.generators import ReportGeneratorFactory
from app.modules.reporting.infrastructure.repository import SQLAlchemyReportRepository
from app.shared.infrastructure.event_registry import EventHandlerRegistry

logger = logging.getLogger(__name__)


class ReportingEventHandler:
    """Handler for reporting-related events"""

    def __init__(self, session_factory: async_sessionmaker = AsyncSessionLocal):
        self.session_factory = session_factory
        self.generator_factory = ReportGeneratorFactory()

    async def handle_report_generation_requested(self, event_data: dict[str, Any]) -> None:
        """Handle ReportGenerationRequestedEvent"""
        report_id = event_data["report_id"]

        async with self.session_factory() as session:
            try:
                repository = SQLAlchemyReportRepository(session)
                data_adapter = ReportingDataAdapter(session)

                # Get the report
                report = await repository.get_by_id(report_id)
                if not report:
                    logger.error(f"Report {report_id} not found")
                    return

                # Check if already completed or processing
                if report.is_completed():
                    logger.info(f"Report {report_id} already completed")
                    return

                if report.is_processing():
                    logger.info(f"Report {report_id} is currently being processed")
                    return

                # Start processing
                report.start_processing()
                await repository.update(report)
                await session.commit()

                logger.info(f"Starting generation of report {report_id}")

                # Fetch data for report
                data = await self._fetch_report_data(report, data_adapter)

                # Generate the report file
                generator = self.generator_factory.get_generator(report.format.value)
                file_path = await generator.generate(report, data)

                # Mark as completed
                report.complete(str(file_path))
                await repository.update(report)
                await session.commit()

                logger.info(f"Report {report_id} generated successfully: {file_path}")

            except Exception as e:
                logger.error(f"Failed to generate report {report_id}: {e}")

                # Mark as failed
                try:
                    report = await repository.get_by_id(report_id)
                    if report:
                        report.fail(str(e))
                        await repository.update(report)
                        await session.commit()
                except Exception as update_error:
                    logger.error(f"Failed to update report status: {update_error}")
                    await session.rollback()

    async def _fetch_report_data(self, report, data_adapter) -> dict[str, Any]:
        """Fetch data for the report based on its type"""
        if report.report_type == ReportType.PAYROLL_SUMMARY:
            return await data_adapter.fetch_payroll_summary_data(report.parameters)
        elif report.report_type == ReportType.EMPLOYEE_COMPENSATION:
            return await data_adapter.fetch_employee_compensation_data(report.parameters)
        elif report.report_type == ReportType.ABSENCE_SUMMARY:
            return await data_adapter.fetch_absence_summary_data(report.parameters)
        elif report.report_type == ReportType.TIMESHEET_SUMMARY:
            return await data_adapter.fetch_timesheet_summary_data(report.parameters)
        elif report.report_type == ReportType.TAX_REPORT:
            return await data_adapter.fetch_tax_report_data(report.parameters)
        else:
            return await data_adapter.fetch_custom_report_data(report.parameters)


def register_reporting_handlers(registry: EventHandlerRegistry) -> None:
    """Register all reporting event handlers"""
    handler = ReportingEventHandler()

    # Register reporting events with new format: module.event-name
    registry.register(
        "reporting.report-generation-requested-event", handler.handle_report_generation_requested
    )

    logger.info("Registered reporting event handlers")
