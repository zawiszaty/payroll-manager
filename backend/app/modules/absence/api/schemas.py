from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.absence.domain.value_objects import AbsenceStatus, AbsenceType


class AbsenceCreate(BaseModel):
    employee_id: UUID
    absence_type: AbsenceType
    start_date: date
    end_date: date
    reason: Optional[str] = None
    notes: Optional[str] = None


class AbsenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: UUID
    absence_type: AbsenceType
    start_date: date
    end_date: date
    status: AbsenceStatus
    reason: Optional[str] = None
    notes: Optional[str] = None


class AbsenceBalanceCreate(BaseModel):
    employee_id: UUID
    absence_type: AbsenceType
    year: int
    total_days: Decimal


class AbsenceBalanceUpdate(BaseModel):
    total_days: Decimal


class AbsenceBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: UUID
    absence_type: AbsenceType
    year: int
    total_days: Decimal
    used_days: Decimal
    remaining_days: Decimal


class AbsenceBalanceDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    employee_id: UUID
    absence_type: AbsenceType
    year: int
    total_days: Decimal
    used_days: Decimal
