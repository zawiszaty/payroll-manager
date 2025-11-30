from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, DateTime, Numeric, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.modules.absence.domain.value_objects import AbsenceStatus, AbsenceType


class AbsenceModel(Base):
    __tablename__ = "absences"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    employee_id: Mapped[UUID] = mapped_column(index=True)
    absence_type: Mapped[AbsenceType] = mapped_column(SQLEnum(AbsenceType, name="absencetype"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[AbsenceStatus] = mapped_column(SQLEnum(AbsenceStatus, name="absencestatus"))
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AbsenceBalanceModel(Base):
    __tablename__ = "absence_balances"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    employee_id: Mapped[UUID] = mapped_column(index=True)
    absence_type: Mapped[AbsenceType] = mapped_column(SQLEnum(AbsenceType, name="absencetype"))
    year: Mapped[int] = mapped_column(index=True)
    total_days: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    used_days: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
