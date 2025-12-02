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
from app.modules.employee.domain.events import EmployeeUpdatedEvent
from app.modules.employee.domain.models import Employee
from app.modules.employee.domain.repository import EmployeeRepository
from app.modules.employee.domain.services import ChangeEmployeeStatusService, CreateEmployeeService
from app.modules.employee.infrastructure.read_model import EmployeeReadModel


class CreateEmployeeHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository
        self.service = CreateEmployeeService()

    async def handle(self, command: CreateEmployeeCommand) -> Employee:
        existing = await self.repository.get_by_email(command.email)
        if existing:
            raise ValueError(f"Employee with email {command.email} already exists")

        employee = self.service.create(
            first_name=command.first_name,
            last_name=command.last_name,
            email=command.email,
            hire_date=command.hire_date,
            phone=command.phone,
            date_of_birth=command.date_of_birth,
        )

        return await self.repository.add(employee)


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

        return await self.repository.update(updated_employee)


class ChangeEmployeeStatusHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository
        self.service = ChangeEmployeeStatusService()

    async def handle(self, command: ChangeEmployeeStatusCommand) -> Employee:
        employee = await self.repository.get_by_id(command.employee_id)
        if not employee:
            raise ValueError(f"Employee {command.employee_id} not found")

        employee = self.service.change_status(
            employee=employee,
            new_status_type=command.new_status,
            effective_date=command.effective_date,
            reason=command.reason,
        )

        return await self.repository.update(employee)


class GetEmployeeHandler:
    def __init__(self, read_model: EmployeeReadModel):
        self.read_model = read_model

    async def handle(self, query: GetEmployeeQuery):
        return await self.read_model.get_by_id(query.employee_id)


class ListEmployeesHandler:
    def __init__(self, read_model: EmployeeReadModel):
        self.read_model = read_model

    async def handle(self, query: ListEmployeesQuery):
        items, total_count = await self.read_model.list(skip=query.skip, limit=query.limit)
        return items, total_count


class GetEmployeeByEmailHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def handle(self, query: GetEmployeeByEmailQuery) -> Optional[Employee]:
        return await self.repository.get_by_email(query.email)
