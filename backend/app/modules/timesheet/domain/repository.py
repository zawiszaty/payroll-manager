from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from app.modules.timesheet.domain.models import Timesheet


class TimesheetRepository(ABC):
    @abstractmethod
    async def save(self, timesheet: Timesheet) -> Timesheet:
        pass

    @abstractmethod
    async def get_by_id(self, timesheet_id: UUID) -> Timesheet | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Timesheet]:
        pass

    @abstractmethod
    async def get_by_employee(self, employee_id: UUID) -> list[Timesheet]:
        pass

    @abstractmethod
    async def get_by_employee_and_date_range(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> list[Timesheet]:
        pass

    @abstractmethod
    async def get_by_status(self, status: str) -> list[Timesheet]:
        pass

    @abstractmethod
    async def get_pending_approval(self) -> list[Timesheet]:
        pass

    @abstractmethod
    async def sum_hours_in_interval(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> float:
        pass

    @abstractmethod
    async def delete(self, timesheet_id: UUID) -> None:
        pass
