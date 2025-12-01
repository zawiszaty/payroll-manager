from abc import ABC, abstractmethod
from pathlib import Path

from app.modules.reporting.domain.entities import Report


class IReportGenerator(ABC):
    @abstractmethod
    async def generate(self, report: Report, data: dict) -> Path:
        pass

    @abstractmethod
    def supports_format(self, format_type: str) -> bool:
        pass
