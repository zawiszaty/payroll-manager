from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.domain.models import User
from app.modules.auth.domain.repository import UserRepository
from app.modules.auth.infrastructure.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        user_model = UserModel.from_domain(user)
        self.session.add(user_model)
        await self.session.flush()
        await self.session.refresh(user_model)
        return user_model.to_domain()

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None

    async def update(self, user: User) -> User:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user.id))
        user_model = result.scalar_one_or_none()
        if not user_model:
            raise ValueError(f"User with id {user.id} not found")

        user_model.email = user.email
        user_model.hashed_password = user.hashed_password
        user_model.role = user.role
        user_model.status = user.status
        user_model.full_name = user.full_name
        user_model.refresh_token = user.refresh_token
        user_model.refresh_token_expires_at = user.refresh_token_expires_at
        user_model.updated_at = user.updated_at

        await self.session.flush()
        await self.session.refresh(user_model)
        return user_model.to_domain()

    async def list_all(self) -> list[User]:
        result = await self.session.execute(select(UserModel))
        user_models = result.scalars().all()
        return [user_model.to_domain() for user_model in user_models]

    async def exists_by_email(self, email: str) -> bool:
        result = await self.session.execute(select(UserModel.id).where(UserModel.email == email))
        return result.scalar_one_or_none() is not None

    async def get_by_refresh_token(self, refresh_token: str) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.refresh_token == refresh_token)
        )
        user_model = result.scalar_one_or_none()
        return user_model.to_domain() if user_model else None
