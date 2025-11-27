import uuid

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base
from app.modules.contract.domain.value_objects import ContractStatus, ContractType


class ContractORM(Base):
    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    contract_type = Column(SQLEnum(ContractType), nullable=False)
    status = Column(SQLEnum(ContractStatus), nullable=False, default=ContractStatus.PENDING)
    version = Column(Integer, nullable=False, default=1)

    rate_amount = Column(Numeric(12, 2), nullable=False)
    rate_currency = Column(String(3), nullable=False, default="USD")

    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True)

    hours_per_week = Column(Integer, nullable=True)
    commission_percentage = Column(Numeric(5, 2), nullable=True)
    description = Column(Text, nullable=True)

    cancellation_reason = Column(String(500), nullable=True)
    canceled_at = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
