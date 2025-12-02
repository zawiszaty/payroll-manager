import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.modules.auth.application.services import AuthenticationService
from app.modules.auth.domain.value_objects import UserRole
from app.modules.auth.infrastructure.dependencies import get_current_active_user
from app.modules.auth.infrastructure.repository import SqlAlchemyUserRepository


def get_test_database_url() -> str:
    """
    Build test database URL from environment variables.

    Required environment variables (with defaults for CI/test):
    - TEST_DB_USER: Database user (default: payroll_user)
    - TEST_DB_PASSWORD: Database password (default: payroll_pass)
    - TEST_DB_HOST: Database host (default: postgres)
    - TEST_DB_PORT: Database port (default: 5432)
    - TEST_DB_NAME: Test database name (default: payroll_db_test)

    Raises:
        RuntimeError: If required variables are missing and no defaults are available.
    """
    db_user = os.getenv("TEST_DB_USER", "payroll_user")
    db_password = os.getenv("TEST_DB_PASSWORD", "payroll_pass")
    db_host = os.getenv("TEST_DB_HOST", "postgres")
    db_port = os.getenv("TEST_DB_PORT", "5432")
    db_name = os.getenv("TEST_DB_NAME", "payroll_db_test")

    # Validate that we have all required values
    if not all([db_user, db_password, db_host, db_port, db_name]):
        missing = []
        if not db_user:
            missing.append("TEST_DB_USER")
        if not db_password:
            missing.append("TEST_DB_PASSWORD")
        if not db_host:
            missing.append("TEST_DB_HOST")
        if not db_port:
            missing.append("TEST_DB_PORT")
        if not db_name:
            missing.append("TEST_DB_NAME")

        raise RuntimeError(
            f"Missing required test database configuration: {', '.join(missing)}. "
            f"Set environment variables or use defaults (TEST_DB_USER, TEST_DB_PASSWORD, "
            f"TEST_DB_HOST, TEST_DB_PORT, TEST_DB_NAME)."
        )

    return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


@pytest_asyncio.fixture
async def test_engine():
    test_database_url = get_test_database_url()
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
    original_overrides = app.dependency_overrides.copy()

    async def override_get_db():
        yield test_session

    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_active_user] = override_get_current_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides = original_overrides


@pytest_asyncio.fixture
async def unauthenticated_client(test_session):
    """Create unauthenticated test client."""
    original_overrides = app.dependency_overrides.copy()

    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides = original_overrides
