from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.reporting.domain.entities import Report
from app.modules.reporting.domain.value_objects import ReportStatus, ReportType


class ReportRepository(ABC):
    @abstractmethod
    async def save(self, report: Report) -> Report:
        pass

    @abstractmethod
    async def get_by_id(self, report_id: UUID) -> Report | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[Report]:
        pass

    @abstractmethod
    async def list_by_type(self, report_type: ReportType) -> list[Report]:
        pass

    @abstractmethod
    async def list_by_status(self, status: ReportStatus) -> list[Report]:
        pass

    @abstractmethod
    async def update(self, report: Report) -> Report:
        pass

    @abstractmethod
    async def delete(self, report_id: UUID) -> None:
        pass
