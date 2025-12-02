from datetime import timedelta
from typing import Optional

from app.modules.employee.application.commands import (
    ChangeEmployeeStatusCommand,
    CreateEmployeeCommand,
    UpdateEmployeeCommand,
)
from app.modules.employee.application.queries import (
    GetEmployeeByEmailQuery,
    GetEmployeeQuery,
    ListEmployeesQuery,
)
from app.modules.employee.domain.events import (
    EmployeeCreatedEvent,
    EmployeeStatusChangedEvent,
    EmployeeUpdatedEvent,
)
from app.modules.employee.domain.models import Employee
from app.modules.employee.domain.repository import EmployeeRepository
from app.modules.employee.domain.value_objects import EmploymentStatus, EmploymentStatusType
from app.modules.employee.infrastructure.read_model import EmployeeReadModel
from app.shared.domain.value_objects import DateRange


class CreateEmployeeHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def handle(self, command: CreateEmployeeCommand) -> Employee:
        existing = await self.repository.get_by_email(command.email)
        if existing:
            raise ValueError(f"Employee with email {command.email} already exists")

        # Create employee
        employee = Employee(
            first_name=command.first_name,
            last_name=command.last_name,
            email=command.email,
            hire_date=command.hire_date,
            phone=command.phone,
            date_of_birth=command.date_of_birth,
        )

        # Add initial ACTIVE status starting from hire date
        initial_status = EmploymentStatus(
            status_type=EmploymentStatusType.ACTIVE,
            date_range=DateRange(valid_from=command.hire_date),
        )
        employee.add_status(initial_status)

        # Add domain event
        employee._add_domain_event(
            EmployeeCreatedEvent(
                employee_id=employee.id,
                first_name=employee.first_name,
                last_name=employee.last_name,
                email=employee.email,
                hire_date=employee.hire_date,
            )
        )

        return await self.repository.save(employee)


class UpdateEmployeeHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def handle(self, command: UpdateEmployeeCommand) -> Employee:
        employee = await self.repository.get_by_id(command.employee_id)
        if not employee:
            raise ValueError(f"Employee {command.employee_id} not found")

        old_values = {}
        new_values = {}

        if command.first_name is not None and command.first_name != employee.first_name:
            old_values["first_name"] = employee.first_name
            new_values["first_name"] = command.first_name

        if command.last_name is not None and command.last_name != employee.last_name:
            old_values["last_name"] = employee.last_name
            new_values["last_name"] = command.last_name

        if command.email is not None and command.email != employee.email:
            old_values["email"] = employee.email
            new_values["email"] = command.email

        if command.phone is not None and command.phone != employee.phone:
            old_values["phone"] = employee.phone
            new_values["phone"] = command.phone

        if command.date_of_birth is not None and command.date_of_birth != employee.date_of_birth:
            old_values["date_of_birth"] = (
                employee.date_of_birth.isoformat() if employee.date_of_birth else None
            )
            new_values["date_of_birth"] = (
                command.date_of_birth.isoformat() if command.date_of_birth else None
            )

        updated_employee = Employee(
            id=employee.id,
            first_name=command.first_name
            if command.first_name is not None
            else employee.first_name,
            last_name=command.last_name if command.last_name is not None else employee.last_name,
            email=command.email if command.email is not None else employee.email,
            phone=command.phone if command.phone is not None else employee.phone,
            date_of_birth=command.date_of_birth
            if command.date_of_birth is not None
            else employee.date_of_birth,
            hire_date=employee.hire_date,
            statuses=employee.statuses,
            created_at=employee.created_at,
            updated_at=employee.updated_at,
        )

        if old_values:
            updated_employee._add_domain_event(
                EmployeeUpdatedEvent(
                    employee_id=employee.id, old_values=old_values, new_values=new_values
                )
            )

        return await self.repository.save(updated_employee)


class ChangeEmployeeStatusHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def handle(self, command: ChangeEmployeeStatusCommand) -> Employee:
        employee = await self.repository.get_by_id(command.employee_id)
        if not employee:
            raise ValueError(f"Employee {command.employee_id} not found")

        # Get current status at the day before effective_date
        # This ensures we close the correct status that's active just before the new one starts
        lookup_date = command.effective_date - timedelta(days=1)
        current_status = employee.get_status_at(lookup_date)
        old_status_value = current_status.status_type.value if current_status else None

        # Close current status (set valid_to to day before effective_date)
        if current_status:
            closed_status = EmploymentStatus(
                status_type=current_status.status_type,
                date_range=DateRange(
                    valid_from=current_status.date_range.valid_from,
                    valid_to=command.effective_date - timedelta(days=1),
                ),
                reason=current_status.reason,
            )
            # Replace the open-ended status with the closed one
            employee.statuses = [
                s
                for s in employee.statuses
                if s.date_range.valid_from != current_status.date_range.valid_from
            ]
            employee.statuses.append(closed_status)

        # Add new status starting from effective_date
        new_status = EmploymentStatus(
            status_type=command.new_status,
            date_range=DateRange(valid_from=command.effective_date),
            reason=command.reason,
        )
        employee.add_status(new_status)

        # Add domain event
        if old_status_value:
            employee._add_domain_event(
                EmployeeStatusChangedEvent(
                    employee_id=employee.id,
                    old_status=old_status_value,
                    new_status=command.new_status.value,
                    status_valid_from=command.effective_date,
                    status_valid_to=new_status.date_range.valid_to,
                    reason=command.reason,
                )
            )

        return await self.repository.save(employee)


class GetEmployeeHandler:
    def __init__(self, read_model: EmployeeReadModel):
        self.read_model = read_model

    async def handle(self, query: GetEmployeeQuery):
        return await self.read_model.get_by_id(query.employee_id)


class ListEmployeesHandler:
    def __init__(self, read_model: EmployeeReadModel):
        self.read_model = read_model

    async def handle(self, query: ListEmployeesQuery):
        items, total_count = await self.read_model.list(page=query.page, limit=query.limit)
        return items, total_count


class GetEmployeeByEmailHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def handle(self, query: GetEmployeeByEmailQuery) -> Optional[Employee]:
        return await self.repository.get_by_email(query.email)
