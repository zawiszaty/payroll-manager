from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Date, Float, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TimesheetORM(Base):
    __tablename__ = "timesheets"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    employee_id: Mapped[UUID] = mapped_column(Uuid, index=True, nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    hours: Mapped[float] = mapped_column(Float, nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overtime_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    project_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    task_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    updated_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    submitted_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    approved_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    approved_by: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
