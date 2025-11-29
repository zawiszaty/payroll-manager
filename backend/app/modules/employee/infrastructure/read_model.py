from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.employee.api.views import (
    EmployeeDetailView,
    EmployeeListView,
    EmploymentStatusView,
)
from app.modules.employee.infrastructure.models import EmployeeORM


class EmployeeReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, employee_id: UUID) -> Optional[EmployeeDetailView]:
        stmt = (
            select(EmployeeORM)
            .options(selectinload(EmployeeORM.statuses))
            .where(EmployeeORM.id == employee_id)
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return EmployeeDetailView(
            id=orm.id,
            first_name=orm.first_name,
            last_name=orm.last_name,
            email=orm.email,
            phone=orm.phone,
            date_of_birth=orm.date_of_birth,
            hire_date=orm.hire_date,
            statuses=[
                EmploymentStatusView(
                    status_type=s.status_type,
                    valid_from=s.valid_from,
                    valid_to=s.valid_to,
                    reason=s.reason,
                )
                for s in sorted(orm.statuses, key=lambda x: x.valid_from, reverse=True)
            ],
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    async def list(self, skip: int = 0, limit: int = 100) -> Tuple[List[EmployeeListView], int]:
        # Get total count
        count_stmt = select(func.count()).select_from(EmployeeORM)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Get paginated items
        stmt = (
            select(EmployeeORM)
            .options(selectinload(EmployeeORM.statuses))
            .offset(skip)
            .limit(limit)
            .order_by(EmployeeORM.created_at.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            EmployeeListView(
                id=orm.id,
                first_name=orm.first_name,
                last_name=orm.last_name,
                email=orm.email,
                hire_date=orm.hire_date,
                current_status=self._get_current_status(orm),
            )
            for orm in orms
        ]

        return items, total_count

    def _get_current_status(self, orm: EmployeeORM):
        from datetime import date

        today = date.today()
        active_statuses = [
            s
            for s in orm.statuses
            if s.valid_from <= today and (s.valid_to is None or s.valid_to >= today)
        ]
        return active_statuses[0].status_type if active_statuses else None
