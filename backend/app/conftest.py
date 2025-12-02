import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.modules.auth.application.services import AuthenticationService
from app.modules.auth.domain.value_objects import UserRole
from app.modules.auth.infrastructure.dependencies import get_current_active_user
from app.modules.auth.infrastructure.repository import SqlAlchemyUserRepository


@pytest_asyncio.fixture
async def test_engine():
    test_database_url = (
        "postgresql+asyncpg://payroll_user:payroll_pass@postgres:5432/payroll_db_test"
    )
    engine = create_async_engine(test_database_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def test_user(test_session):
    """Create a test user for authentication."""
    repository = SqlAlchemyUserRepository(test_session)
    auth_service = AuthenticationService(repository)

    user = await auth_service.create_user(
        email="test@example.com",
        password="testpassword123",
        role=UserRole.ADMIN,
        full_name="Test User",
    )
    await test_session.commit()

    return user


@pytest_asyncio.fixture
async def auth_headers(test_user):
    """Create authentication headers with access token."""
    from datetime import timedelta

    from app.config import get_settings

    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthenticationService.create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email, "role": test_user.role.value},
        expires_delta=access_token_expires,
    )

    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def client(test_session, test_user):
    """Create authenticated test client."""

    async def override_get_db():
        yield test_session

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauthenticated_client(test_session):
    """Create unauthenticated test client."""

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
