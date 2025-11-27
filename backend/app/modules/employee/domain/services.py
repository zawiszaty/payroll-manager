from datetime import date
from typing import Optional

from app.modules.employee.domain.models import Employee
from app.modules.employee.domain.value_objects import EmploymentStatus, EmploymentStatusType
from app.shared.domain.value_objects import DateRange


class CreateEmployeeService:
    def create(
        self, first_name: str, last_name: str, email: str, hire_date: date, **kwargs
    ) -> Employee:
        employee = Employee(
            first_name=first_name, last_name=last_name, email=email, hire_date=hire_date, **kwargs
        )

        initial_status = EmploymentStatus(
            status_type=EmploymentStatusType.ACTIVE, date_range=DateRange(valid_from=hire_date)
        )
        employee.add_status(initial_status)

        return employee


class ChangeEmployeeStatusService:
    def change_status(
        self,
        employee: Employee,
        new_status_type: EmploymentStatusType,
        effective_date: date,
        reason: Optional[str] = None,
    ) -> Employee:
        from datetime import timedelta

        current_status = employee.get_status_at(date.today())
        if current_status:
            closed_status = EmploymentStatus(
                status_type=current_status.status_type,
                date_range=DateRange(
                    valid_from=current_status.date_range.valid_from,
                    valid_to=effective_date - timedelta(days=1),
                ),
                reason=current_status.reason,
            )
            employee.statuses = [
                s
                for s in employee.statuses
                if s.date_range.valid_from != current_status.date_range.valid_from
            ]
            employee.statuses.append(closed_status)

        new_status = EmploymentStatus(
            status_type=new_status_type,
            date_range=DateRange(valid_from=effective_date),
            reason=reason,
        )
        employee.add_status(new_status)

        return employee
