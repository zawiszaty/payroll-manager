from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.compensation.api.views import BonusView, RateView
from app.modules.compensation.infrastructure.models import BonusORM, RateORM


class RateReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, rate_id: UUID) -> Optional[RateView]:
        stmt = select(RateORM).where(RateORM.id == rate_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return RateView(
            id=orm.id,
            employee_id=orm.employee_id,
            rate_type=orm.rate_type,
            amount=orm.amount,
            currency=orm.currency,
            valid_from=orm.valid_from,
            valid_to=orm.valid_to,
            description=orm.description,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    async def list(self, skip: int = 0, limit: int = 100) -> List[RateView]:
        stmt = select(RateORM).offset(skip).limit(limit).order_by(RateORM.created_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            RateView(
                id=orm.id,
                employee_id=orm.employee_id,
                rate_type=orm.rate_type,
                amount=orm.amount,
                currency=orm.currency,
                valid_from=orm.valid_from,
                valid_to=orm.valid_to,
                description=orm.description,
                created_at=orm.created_at.date() if orm.created_at else None,
                updated_at=orm.updated_at.date() if orm.updated_at else None,
            )
            for orm in orms
        ]

    async def get_by_employee(self, employee_id: UUID) -> List[RateView]:
        stmt = (
            select(RateORM)
            .where(RateORM.employee_id == employee_id)
            .order_by(RateORM.valid_from.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            RateView(
                id=orm.id,
                employee_id=orm.employee_id,
                rate_type=orm.rate_type,
                amount=orm.amount,
                currency=orm.currency,
                valid_from=orm.valid_from,
                valid_to=orm.valid_to,
                description=orm.description,
                created_at=orm.created_at.date() if orm.created_at else None,
                updated_at=orm.updated_at.date() if orm.updated_at else None,
            )
            for orm in orms
        ]

    async def get_active_rate(self, employee_id: UUID, check_date: date) -> Optional[RateView]:
        stmt = (
            select(RateORM)
            .where(RateORM.employee_id == employee_id)
            .where(RateORM.valid_from <= check_date)
            .where((RateORM.valid_to.is_(None)) | (RateORM.valid_to >= check_date))
            .order_by(RateORM.valid_from.desc())
        )
        result = await self.session.execute(stmt)
        orm = result.scalars().first()

        if not orm:
            return None

        return RateView(
            id=orm.id,
            employee_id=orm.employee_id,
            rate_type=orm.rate_type,
            amount=orm.amount,
            currency=orm.currency,
            valid_from=orm.valid_from,
            valid_to=orm.valid_to,
            description=orm.description,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )


class BonusReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, bonus_id: UUID) -> Optional[BonusView]:
        stmt = select(BonusORM).where(BonusORM.id == bonus_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return BonusView(
            id=orm.id,
            employee_id=orm.employee_id,
            bonus_type=orm.bonus_type,
            amount=orm.amount,
            currency=orm.currency,
            payment_date=orm.payment_date,
            description=orm.description,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=None,
        )

    async def list(self, skip: int = 0, limit: int = 100) -> List[BonusView]:
        stmt = select(BonusORM).offset(skip).limit(limit).order_by(BonusORM.created_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            BonusView(
                id=orm.id,
                employee_id=orm.employee_id,
                bonus_type=orm.bonus_type,
                amount=orm.amount,
                currency=orm.currency,
                payment_date=orm.payment_date,
                description=orm.description,
                created_at=orm.created_at.date() if orm.created_at else None,
                updated_at=None,
            )
            for orm in orms
        ]

    async def get_by_employee(self, employee_id: UUID) -> List[BonusView]:
        stmt = (
            select(BonusORM)
            .where(BonusORM.employee_id == employee_id)
            .order_by(BonusORM.payment_date.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            BonusView(
                id=orm.id,
                employee_id=orm.employee_id,
                bonus_type=orm.bonus_type,
                amount=orm.amount,
                currency=orm.currency,
                payment_date=orm.payment_date,
                description=orm.description,
                created_at=orm.created_at.date() if orm.created_at else None,
                updated_at=None,
            )
            for orm in orms
        ]
