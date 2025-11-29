"""
SQLAlchemy ORM models for Payroll module
"""

import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.modules.payroll.domain.value_objects import (
    PayrollLineType,
    PayrollPeriodType,
    PayrollStatus,
)


class PayrollORM(Base):
    """ORM model for Payroll aggregate"""

    __tablename__ = "payrolls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Period information
    period_type = Column(SQLEnum(PayrollPeriodType), nullable=False)
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    # Status
    status = Column(SQLEnum(PayrollStatus), nullable=False, default=PayrollStatus.DRAFT)

    # Calculation results
    gross_pay = Column(Numeric(10, 2), nullable=False, default=0)
    total_deductions = Column(Numeric(10, 2), nullable=False, default=0)
    total_taxes = Column(Numeric(10, 2), nullable=False, default=0)
    net_pay = Column(Numeric(10, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="USD")

    # Approval and payment tracking
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    payment_reference = Column(String(255), nullable=True)

    # Notes and metadata
    notes = Column(Text, nullable=True)
    version = Column(String(50), nullable=False, default="1")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    lines = relationship(
        "PayrollLineORM", back_populates="payroll", cascade="all, delete-orphan"
    )


class PayrollLineORM(Base):
    """ORM model for Payroll line items"""

    __tablename__ = "payroll_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payroll_id = Column(UUID(as_uuid=True), ForeignKey("payrolls.id"), nullable=False)

    # Line details
    line_type = Column(SQLEnum(PayrollLineType), nullable=False)
    description = Column(String(500), nullable=False)
    quantity = Column(Numeric(10, 4), nullable=False)  # hours, days, units
    rate = Column(Numeric(10, 2), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")

    # Reference to source entity (contract, bonus, etc.)
    reference_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    payroll = relationship("PayrollORM", back_populates="lines")
