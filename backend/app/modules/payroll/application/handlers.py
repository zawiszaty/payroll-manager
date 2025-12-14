from typing import Optional

from app.modules.payroll.application.commands import (
    ApprovePayrollCommand,
    CalculatePayrollCommand,
    CreatePayrollCommand,
    MarkPayrollAsPaidCommand,
    ProcessPayrollCommand,
    UpdatePayrollStatusCommand,
)
from app.modules.payroll.application.queries import (
    GetPayrollQuery,
    ListPayrollsByEmployeeQuery,
    ListPayrollsQuery,
)
from app.modules.payroll.domain.models import Payroll
from app.modules.payroll.domain.repository import PayrollRepository
from app.modules.payroll.domain.services import PayrollCalculationService
from app.modules.payroll.domain.value_objects import PayrollPeriod
from app.modules.payroll.infrastructure.adapters import PayrollValidationAdapter
from app.modules.payroll.infrastructure.read_model import PayrollReadModel
from app.modules.payroll.presentation.views import PayrollDetailView


class CreatePayrollHandler:
    def __init__(self, repository: PayrollRepository, validation_adapter: PayrollValidationAdapter):
        self.repository = repository
        self.validation_adapter = validation_adapter

    async def handle(self, command: CreatePayrollCommand) -> Payroll:
        # Validate employee can have payroll created
        can_create, reason = await self.validation_adapter.can_create_payroll(
            command.employee_id, command.period_start_date
        )
        if not can_create:
            raise ValueError(f"Cannot create payroll: {reason}")

        # Validate period
        can_process, reason = await self.validation_adapter.validate_payroll_period(
            command.employee_id, command.period_start_date, command.period_end_date
        )
        if not can_process:
            raise ValueError(f"Invalid payroll period: {reason}")

        # Create payroll
        period = PayrollPeriod(
            period_type=command.period_type,
            start_date=command.period_start_date,
            end_date=command.period_end_date,
        )

        payroll = Payroll.create(
            employee_id=command.employee_id, period=period, notes=command.notes
        )

        return await self.repository.save(payroll)


class CalculatePayrollHandler:
    def __init__(
        self, repository: PayrollRepository, calculation_service: PayrollCalculationService
    ):
        self.repository = repository
        self.calculation_service = calculation_service

    async def handle(self, command: CalculatePayrollCommand) -> Payroll:
        payroll = await self.repository.get_by_id(command.payroll_id)
        if not payroll:
            raise ValueError(f"Payroll {command.payroll_id} not found")

        # Auto-calculate working days if not provided
        from app.modules.payroll.domain.services import PayrollPeriodService

        working_days = command.working_days
        if working_days is None:
            working_days = PayrollPeriodService.get_working_days(
                payroll.period.start_date, payroll.period.end_date
            )

        # Calculate payroll using domain service
        payroll = await self.calculation_service.calculate_payroll(
            payroll, working_days=working_days
        )

        # Automatically submit for approval after calculation
        payroll.submit_for_approval()

        return await self.repository.save(payroll)


class ApprovePayrollHandler:
    def __init__(self, repository: PayrollRepository):
        self.repository = repository

    async def handle(self, command: ApprovePayrollCommand) -> Payroll:
        payroll = await self.repository.get_by_id(command.payroll_id)
        if not payroll:
            raise ValueError(f"Payroll {command.payroll_id} not found")

        payroll.approve(command.approved_by)
        return await self.repository.save(payroll)


class ProcessPayrollHandler:
    def __init__(self, repository: PayrollRepository):
        self.repository = repository

    async def handle(self, command: ProcessPayrollCommand) -> Payroll:
        payroll = await self.repository.get_by_id(command.payroll_id)
        if not payroll:
            raise ValueError(f"Payroll {command.payroll_id} not found")

        payroll.process()
        return await self.repository.save(payroll)


class MarkPayrollAsPaidHandler:
    def __init__(self, repository: PayrollRepository):
        self.repository = repository

    async def handle(self, command: MarkPayrollAsPaidCommand) -> Payroll:
        payroll = await self.repository.get_by_id(command.payroll_id)
        if not payroll:
            raise ValueError(f"Payroll {command.payroll_id} not found")

        payroll.mark_as_paid(command.payment_reference)
        return await self.repository.save(payroll)


class UpdatePayrollStatusHandler:
    def __init__(self, repository: PayrollRepository):
        self.repository = repository

    async def handle(self, command: UpdatePayrollStatusCommand) -> Payroll:
        payroll = await self.repository.get_by_id(command.payroll_id)
        if not payroll:
            raise ValueError(f"Payroll {command.payroll_id} not found")

        # Simple status update - could add validation here
        payroll.status = command.new_status
        return await self.repository.save(payroll)


# Query handlers
class GetPayrollHandler:
    def __init__(self, read_model: PayrollReadModel):
        self.read_model = read_model

    async def handle(self, query: GetPayrollQuery) -> Optional[PayrollDetailView]:
        return await self.read_model.get_by_id(query.payroll_id)


class ListPayrollsHandler:
    def __init__(self, read_model: PayrollReadModel):
        self.read_model = read_model

    async def handle(self, query: ListPayrollsQuery):
        items, total_count = await self.read_model.list(page=query.page, limit=query.limit)
        return items, total_count


class ListPayrollsByEmployeeHandler:
    def __init__(self, read_model: PayrollReadModel):
        self.read_model = read_model

    async def handle(self, query: ListPayrollsByEmployeeQuery):
        items, total_count = await self.read_model.list_by_employee(
            query.employee_id, page=query.page, limit=query.limit
        )
        return items, total_count
