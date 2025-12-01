from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetReportQuery:
    report_id: UUID


@dataclass
class ListReportsQuery:
    pass


@dataclass
class ListReportsByTypeQuery:
    report_type: str


@dataclass
class ListReportsByStatusQuery:
    status: str
