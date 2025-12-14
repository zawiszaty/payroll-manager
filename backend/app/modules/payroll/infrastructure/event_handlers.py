import logging
from typing import Any

from app.database import get_db
from app.modules.employee.api.facade import EmployeeModuleFacade
from app.modules.employee.infrastructure.read_model import EmployeeReadModel
from app.modules.payroll.application.commands import CreatePayrollCommand
from app.modules.payroll.application.handlers import CreatePayrollHandler
from app.modules.payroll.domain.services import PayrollCalculationService, PayrollPeriodService
from app.modules.payroll.domain.value_objects import PayrollPeriod, PayrollPeriodType
from app.modules.payroll.infrastructure.adapters import PayrollDataGatheringAdapter
from app.modules.payroll.infrastructure.repository import SQLAlchemyPayrollRepository
from app.shared.infrastructure.event_registry import EventHandlerRegistry

logger = logging.getLogger(__name__)


class PayrollEventHandler:
    async def handle_month_end(self, event_data: dict[str, Any]) -> None:
        """
        Handle MonthEndEvent: automatically create and calculate payroll for all active employees
        """
        try:
            from datetime import date as date_type

            year = event_data["year"]
            month = event_data["month"]

            # Parse dates from strings (they're serialized to JSON)
            period_start_str = event_data["period_start"]
            period_end_str = event_data["period_end"]

            if isinstance(period_start_str, str):
                period_start = date_type.fromisoformat(period_start_str)
            else:
                period_start = period_start_str

            if isinstance(period_end_str, str):
                period_end = date_type.fromisoformat(period_end_str)
            else:
                period_end = period_end_str

            logger.info(f"Processing month-end payroll for {year}-{month:02d}")

            # Get the monthly period
            period = PayrollPeriod(
                period_type=PayrollPeriodType.MONTHLY,
                start_date=period_start,
                end_date=period_end,
            )

            # Calculate working days
            working_days = PayrollPeriodService.get_working_days(period_start, period_end)

            # Get all active employees at the end of the period
            async for session in get_db():
                try:
                    # Get active employees
                    employee_facade = EmployeeModuleFacade(session)
                    read_model = EmployeeReadModel(session)

                    # Get all employees (we'll filter active ones)
                    all_employees, total_count = await read_model.list(page=1, limit=1000)
                    logger.info(f"Found {total_count} total employees")

                    # Filter to only active employees
                    active_employees = []
                    for emp in all_employees:
                        is_active = await employee_facade.is_employee_active_on_date(
                            emp.id, period_end
                        )
                        if is_active:
                            active_employees.append(emp)

                    logger.info(f"Found {len(active_employees)} active employees")

                    # Create and calculate payroll for each active employee
                    for employee in active_employees:
                        try:
                            employee_id = employee.id

                            # Check eligibility
                            adapter = PayrollDataGatheringAdapter(session)
                            can_process = await adapter.validate_payroll_eligibility(
                                employee_id, period_start
                            )

                            if not can_process:
                                logger.info(
                                    f"Skipping payroll for employee {employee_id} - not eligible"
                                )
                                continue

                            # Create payroll
                            repository = SQLAlchemyPayrollRepository(session)
                            create_handler = CreatePayrollHandler(repository)

                            command = CreatePayrollCommand(
                                employee_id=employee_id,
                                period=period,
                                notes=f"Auto-generated for {year}-{month:02d}",
                            )

                            payroll = await create_handler.handle(command)

                            # Calculate payroll
                            calculation_service = PayrollCalculationService(adapter)
                            calculated_payroll = await calculation_service.calculate_payroll(
                                payroll, working_days
                            )

                            logger.info(
                                f"Created and calculated payroll {calculated_payroll.id} "
                                f"for employee {employee_id}"
                            )

                        except Exception as e:
                            logger.error(
                                f"Error processing payroll for employee {employee.id}: {e}",
                                exc_info=True,
                            )
                            # Continue processing other employees
                            continue

                    await session.commit()
                    logger.info(f"Completed month-end payroll processing for {year}-{month:02d}")
                    break

                except Exception as e:
                    await session.rollback()
                    logger.error(f"Error in month-end payroll processing: {e}", exc_info=True)
                    raise

        except Exception as e:
            logger.error(f"Error handling month-end event: {e}", exc_info=True)


def register_payroll_handlers(registry: EventHandlerRegistry) -> None:
    handler = PayrollEventHandler()

    # Register month-end event handler
    registry.register("payroll.month-end-event", handler.handle_month_end)

    logger.info("Registered payroll event handlers")
