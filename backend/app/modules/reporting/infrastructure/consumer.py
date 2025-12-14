import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, AbstractRobustConnection
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.modules.reporting.domain.value_objects import ReportType
from app.modules.reporting.infrastructure.adapters import ReportingDataAdapter
from app.modules.reporting.infrastructure.generators import ReportGeneratorFactory
from app.modules.reporting.infrastructure.repository import SQLAlchemyReportRepository

logger = logging.getLogger(__name__)
settings = get_settings()


class ReportGenerationConsumer:
    def __init__(self, session_factory: async_sessionmaker = AsyncSessionLocal):
        self.session_factory = session_factory
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None
        self.generator_factory = ReportGeneratorFactory()

    async def connect(self) -> None:
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=1)  # Process one report at a time

            exchange = await self.channel.declare_exchange(
                "domain_events", aio_pika.ExchangeType.TOPIC, durable=True
            )

            queue = await self.channel.declare_queue("report_generation", durable=True)

            # Bind to report generation events using wildcard
            # Format: event.payroll-manager.reporting.#
            await queue.bind(exchange, routing_key="event.payroll-manager.reporting.#")

            logger.info("Report generation consumer connected to RabbitMQ")
            await queue.consume(self.process_message)
        except Exception as e:
            logger.error(f"Failed to connect report generation consumer: {e}")
            raise

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process():
            try:
                event_data = json.loads(message.body.decode())
                routing_key = message.routing_key

                # Parse routing key: event.payroll-manager.reporting.event-name
                # Convert kebab-case event name to PascalCase for backward compatibility
                if routing_key is None:
                    logger.warning("Routing key is None")
                    return

                parts = routing_key.split(".")
                if len(parts) >= 4:
                    event_name_kebab = ".".join(parts[3:])
                    event_type = self._kebab_to_pascal_case(event_name_kebab)
                else:
                    # Fallback for old format
                    event_type = routing_key.replace("event.", "")

                await self.handle_event(event_type, event_data)
                logger.debug(f"Processed report generation event: {event_type}")
            except Exception as e:
                logger.error(f"Failed to process report generation event: {e}")

    def _kebab_to_pascal_case(self, text: str) -> str:
        """Convert kebab-case to PascalCase (e.g., report-generation-requested-event -> ReportGenerationRequestedEvent)"""
        return "".join(word.capitalize() for word in text.split("-"))

    async def handle_event(self, event_type: str, event_data: dict) -> None:
        if event_type == "ReportGenerationRequestedEvent":
            await self.generate_report(event_data)
        else:
            logger.warning(f"Unknown event type: {event_type}")

    async def generate_report(self, event_data: dict) -> None:
        """Generate the report asynchronously"""
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
                await repository.save(report)
                await session.commit()

                logger.info(f"Starting generation of report {report_id}")

                # Fetch data for report
                data = await self._fetch_report_data(report, data_adapter)

                # Generate the report file
                generator = self.generator_factory.get_generator(report.format.value)
                file_path = await generator.generate(report, data)

                # Mark as completed
                report.complete(str(file_path))
                await repository.save(report)
                await session.commit()

                logger.info(f"Report {report_id} generated successfully: {file_path}")

            except Exception as e:
                logger.error(f"Failed to generate report {report_id}: {e}")

                # Mark as failed
                try:
                    report = await repository.get_by_id(report_id)
                    if report:
                        report.fail(str(e))
                        await repository.save(report)
                        await session.commit()
                except Exception as update_error:
                    logger.error(f"Failed to update report status: {update_error}")
                    await session.rollback()

    async def _fetch_report_data(self, report, data_adapter) -> dict:
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

    async def close(self) -> None:
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Report generation consumer disconnected")


async def start_report_generation_consumer():
    consumer = ReportGenerationConsumer()
    await consumer.connect()

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        await consumer.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_report_generation_consumer())
