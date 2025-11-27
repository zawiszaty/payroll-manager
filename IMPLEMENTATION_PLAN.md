# Payroll Manager - Detailed Implementation Plan

## Project Structure Overview

```
payroll-manager/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI application entry point
│   │   ├── config.py                    # Configuration management
│   │   ├── database.py                  # SQLAlchemy setup
│   │   ├── dependencies.py              # FastAPI dependencies
│   │   ├── api/                         # API layer
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py            # Main API router
│   │   │   │   ├── employees.py
│   │   │   │   ├── contracts.py
│   │   │   │   ├── compensation.py
│   │   │   │   ├── absences.py
│   │   │   │   ├── timesheets.py
│   │   │   │   ├── payroll.py
│   │   │   │   └── reports.py
│   │   ├── domain/                      # Domain layer (DDD)
│   │   │   ├── __init__.py
│   │   │   ├── employee/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py            # Employee entity
│   │   │   │   ├── value_objects.py     # EmploymentStatus, etc.
│   │   │   │   ├── repository.py        # Repository interface
│   │   │   │   ├── services.py          # Domain services
│   │   │   │   └── events.py            # Domain events
│   │   │   ├── contract/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py            # Contract entity
│   │   │   │   ├── value_objects.py     # ContractStatus, ContractType
│   │   │   │   ├── repository.py
│   │   │   │   ├── services.py          # CreateContract, CancelContract, ExpireContract
│   │   │   │   └── events.py
│   │   │   ├── compensation/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py            # Rate, Bonus, Commission
│   │   │   │   ├── value_objects.py
│   │   │   │   ├── repository.py
│   │   │   │   └── services.py
│   │   │   ├── absence/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py            # Absence entity
│   │   │   │   ├── value_objects.py     # AbsenceType
│   │   │   │   ├── repository.py
│   │   │   │   └── services.py
│   │   │   ├── timesheet/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py            # TimesheetEntry entity
│   │   │   │   ├── repository.py
│   │   │   │   └── services.py
│   │   │   ├── payroll/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py            # PayrollRun, PayrollResult
│   │   │   │   ├── repository.py
│   │   │   │   ├── services.py          # ComputePayrollService
│   │   │   │   └── calculator.py        # Payroll calculation logic
│   │   │   └── shared/
│   │   │       ├── __init__.py
│   │   │       └── value_objects.py     # DateRange, Money
│   │   ├── infrastructure/              # Infrastructure layer
│   │   │   ├── __init__.py
│   │   │   ├── persistence/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py            # SQLAlchemy ORM models
│   │   │   │   ├── employee_repository.py
│   │   │   │   ├── contract_repository.py
│   │   │   │   ├── compensation_repository.py
│   │   │   │   ├── absence_repository.py
│   │   │   │   ├── timesheet_repository.py
│   │   │   │   └── payroll_repository.py
│   │   │   ├── messaging/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── rabbitmq.py          # RabbitMQ connection
│   │   │   │   ├── publisher.py         # Event publisher
│   │   │   │   ├── consumer.py          # Event consumer base
│   │   │   │   └── schemas.py           # Message schemas
│   │   │   └── cache/
│   │   │       ├── __init__.py
│   │   │       └── redis_client.py
│   │   ├── application/                 # Application services layer
│   │   │   ├── __init__.py
│   │   │   ├── employee/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── commands.py          # CreateEmployee, UpdateEmployee
│   │   │   │   ├── queries.py           # GetEmployee, ListEmployees
│   │   │   │   └── handlers.py          # Command/Query handlers
│   │   │   ├── contract/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── commands.py
│   │   │   │   ├── queries.py
│   │   │   │   └── handlers.py
│   │   │   ├── compensation/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── commands.py
│   │   │   │   ├── queries.py
│   │   │   │   └── handlers.py
│   │   │   ├── absence/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── commands.py
│   │   │   │   ├── queries.py
│   │   │   │   └── handlers.py
│   │   │   ├── timesheet/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── commands.py
│   │   │   │   ├── queries.py
│   │   │   │   └── handlers.py
│   │   │   ├── payroll/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── commands.py
│   │   │   │   ├── queries.py
│   │   │   │   └── handlers.py
│   │   │   └── reporting/
│   │   │       ├── __init__.py
│   │   │       ├── queries.py
│   │   │       └── handlers.py
│   │   ├── workers/                     # Background workers
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py           # Celery configuration
│   │   │   ├── tasks/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── contract_expiration.py
│   │   │   │   ├── payroll_processing.py
│   │   │   │   └── event_handlers.py
│   │   │   └── consumers/
│   │   │       ├── __init__.py
│   │   │       ├── employee_consumer.py
│   │   │       ├── contract_consumer.py
│   │   │       ├── timesheet_consumer.py
│   │   │       └── absence_consumer.py
│   │   └── security/
│   │       ├── __init__.py
│   │       ├── auth.py                  # JWT authentication
│   │       ├── roles.py                 # RBAC
│   │       └── dependencies.py
│   ├── migrations/                      # Alembic migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                  # Pytest fixtures
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── store/                       # Redux store
│   │   │   ├── index.ts
│   │   │   ├── api.ts                   # RTK Query API
│   │   │   └── slices/
│   │   │       ├── employeesSlice.ts
│   │   │       ├── contractsSlice.ts
│   │   │       ├── payrollSlice.ts
│   │   │       └── authSlice.ts
│   │   ├── components/
│   │   ├── pages/
│   │   ├── types/
│   │   └── utils/
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── project.md
```

---

## M1: Foundation (Week 1)

### Objectives
- Set up repository structure
- Configure Docker Compose for all services
- Create backend skeleton with DDD structure
- Create frontend skeleton with Redux Toolkit
- Set up CI pipeline

### Backend Tasks

#### 1.1: Repository & Docker Setup
**Files to create:**
- `.gitignore`
- `README.md`
- `docker-compose.yml`
- `.env.example`
- `backend/Dockerfile`
- `frontend/Dockerfile`

**Docker Compose Services:**
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: payroll_db
      POSTGRES_USER: payroll_user
      POSTGRES_PASSWORD: payroll_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  rabbitmq:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: payroll
      RABBITMQ_DEFAULT_PASS: payroll
    ports:
      - "5672:5672"
      - "15672:15672"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - rabbitmq
      - redis
    environment:
      DATABASE_URL: postgresql://payroll_user:payroll_pass@postgres:5432/payroll_db
      RABBITMQ_URL: amqp://payroll:payroll@rabbitmq:5672/
      REDIS_URL: redis://redis:6379/0

  worker:
    build: ./backend
    command: celery -A app.workers.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - rabbitmq
      - redis

  migrations:
    build: ./backend
    command: alembic upgrade head
    volumes:
      - ./backend:/app
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

#### 1.2: Backend Core Configuration
**Files to create:**

**`backend/requirements.txt`:**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
pydantic==2.5.3
pydantic-settings==2.1.0
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
celery==5.3.4
redis==5.0.1
pika==1.3.2
httpx==0.26.0
pytest==7.4.3
pytest-asyncio==0.23.3
pytest-cov==4.1.0
testcontainers==3.7.1
ruff==0.1.11
mypy==1.8.0
```

**`backend/app/config.py`:**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Payroll Manager"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # RabbitMQ
    RABBITMQ_URL: str
    RABBITMQ_EXCHANGE_EMPLOYEE: str = "employee.events"
    RABBITMQ_EXCHANGE_CONTRACT: str = "contract.events"

    # Redis
    REDIS_URL: str

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

**`backend/app/database.py`:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings

settings = get_settings()

# Convert postgresql:// to postgresql+asyncpg://
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

**`backend/app/main.py`:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1.router import api_router

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**`backend/app/api/v1/router.py`:**
```python
from fastapi import APIRouter

api_router = APIRouter()

# Will include sub-routers later
# api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
```

#### 1.3: Alembic Setup
**Commands to run:**
```bash
cd backend
alembic init migrations
```

**`backend/alembic.ini`:** (update)
```ini
sqlalchemy.url = postgresql://payroll_user:payroll_pass@postgres:5432/payroll_db
```

**`backend/migrations/env.py`:** (update to use async)
```python
from app.database import Base
from app.infrastructure.persistence.models import *  # Import all ORM models
```

#### 1.4: DDD Folder Structure
**Create all empty __init__.py files in:**
- `app/domain/employee/`
- `app/domain/contract/`
- `app/domain/compensation/`
- `app/domain/absence/`
- `app/domain/timesheet/`
- `app/domain/payroll/`
- `app/domain/shared/`
- `app/infrastructure/persistence/`
- `app/infrastructure/messaging/`
- `app/infrastructure/cache/`
- `app/application/employee/`
- `app/application/contract/`
- `app/application/compensation/`
- `app/application/absence/`
- `app/application/timesheet/`
- `app/application/payroll/`
- `app/application/reporting/`
- `app/workers/tasks/`
- `app/workers/consumers/`
- `app/security/`

### Frontend Tasks

#### 1.5: React + TypeScript + Vite Setup
**Commands:**
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install @reduxjs/toolkit react-redux
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**`frontend/package.json`:** (additional dependencies)
```json
{
  "dependencies": {
    "@reduxjs/toolkit": "^2.0.1",
    "react-redux": "^9.0.4",
    "react-router-dom": "^6.21.1",
    "axios": "^1.6.5"
  }
}
```

**`frontend/src/store/index.ts`:**
```typescript
import { configureStore } from '@reduxjs/toolkit';
import { api } from './api';

export const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
    // Add other reducers here
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

**`frontend/src/store/api.ts`:**
```typescript
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: 'http://localhost:8000/api/v1',
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('token');
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Employee', 'Contract', 'Payroll', 'Report'],
  endpoints: () => ({}),
});
```

#### 1.6: CI Pipeline Setup
**`.github/workflows/ci.yml`:**
```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install ruff mypy
          pip install -r requirements.txt
      - name: Run ruff
        run: cd backend && ruff check .
      - name: Run mypy
        run: cd backend && mypy app/

  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: cd backend && pytest --cov=app --cov-report=term-missing

  frontend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Run lint
        run: cd frontend && npm run lint

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Run tests
        run: cd frontend && npm test
```

---

## M2: Employee Context (Week 2)

### Objectives
- Implement Employee bounded context
- Create Employee entity with employment status tracking
- Implement CRUD operations
- Create API endpoints
- Write integration tests

### Backend Implementation

#### 2.1: Domain Layer - Employee

**`backend/app/domain/shared/value_objects.py`:**
```python
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class DateRange:
    """Value object for date ranges with validation."""
    valid_from: date
    valid_to: Optional[date] = None

    def __post_init__(self):
        if self.valid_to and self.valid_from > self.valid_to:
            raise ValueError("valid_from must be before valid_to")

    def is_active_at(self, check_date: date) -> bool:
        """Check if this range is active at the given date."""
        if check_date < self.valid_from:
            return False
        if self.valid_to and check_date > self.valid_to:
            return False
        return True

    def overlaps_with(self, other: 'DateRange') -> bool:
        """Check if this range overlaps with another."""
        if self.valid_to and other.valid_from > self.valid_to:
            return False
        if other.valid_to and self.valid_from > other.valid_to:
            return False
        return True

@dataclass(frozen=True)
class Money:
    """Value object for monetary amounts."""
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
```

**`backend/app/domain/employee/value_objects.py`:**
```python
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional
from app.domain.shared.value_objects import DateRange

class EmploymentStatusType(str, Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"

@dataclass(frozen=True)
class EmploymentStatus:
    """Value object for employment status."""
    status_type: EmploymentStatusType
    date_range: DateRange
    reason: Optional[str] = None

    def is_active_at(self, check_date: date) -> bool:
        """Check if this status is active at the given date."""
        return self.date_range.is_active_at(check_date)
```

**`backend/app/domain/employee/models.py`:**
```python
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List
from uuid import UUID, uuid4
from app.domain.employee.value_objects import EmploymentStatus, EmploymentStatusType

@dataclass
class Employee:
    """Employee aggregate root."""
    id: UUID = field(default_factory=uuid4)
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    hire_date: Optional[date] = None
    statuses: List[EmploymentStatus] = field(default_factory=list)
    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)

    def add_status(self, status: EmploymentStatus) -> None:
        """Add a new employment status."""
        # Validate no overlapping statuses
        for existing_status in self.statuses:
            if existing_status.date_range.overlaps_with(status.date_range):
                raise ValueError("Status periods cannot overlap")

        self.statuses.append(status)
        self.updated_at = date.today()

    def get_status_at(self, check_date: date) -> Optional[EmploymentStatus]:
        """Get the employment status at a specific date."""
        for status in self.statuses:
            if status.is_active_at(check_date):
                return status
        return None

    def is_active_at(self, check_date: date) -> bool:
        """Check if employee is active at a specific date."""
        status = self.get_status_at(check_date)
        return status is not None and status.status_type == EmploymentStatusType.ACTIVE

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

**`backend/app/domain/employee/repository.py`:**
```python
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.domain.employee.models import Employee

class EmployeeRepository(ABC):
    """Repository interface for Employee aggregate."""

    @abstractmethod
    async def add(self, employee: Employee) -> Employee:
        """Add a new employee."""
        pass

    @abstractmethod
    async def get_by_id(self, employee_id: UUID) -> Optional[Employee]:
        """Get employee by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email."""
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """List employees with pagination."""
        pass

    @abstractmethod
    async def update(self, employee: Employee) -> Employee:
        """Update employee."""
        pass

    @abstractmethod
    async def delete(self, employee_id: UUID) -> bool:
        """Delete employee."""
        pass
```

**`backend/app/domain/employee/services.py`:**
```python
from datetime import date
from app.domain.employee.models import Employee
from app.domain.employee.value_objects import EmploymentStatus, EmploymentStatusType
from app.domain.shared.value_objects import DateRange

class CreateEmployeeService:
    """Domain service for creating employees."""

    def create(
        self,
        first_name: str,
        last_name: str,
        email: str,
        hire_date: date,
        **kwargs
    ) -> Employee:
        """Create a new employee with initial active status."""
        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hire_date=hire_date,
            **kwargs
        )

        # Add initial active status
        initial_status = EmploymentStatus(
            status_type=EmploymentStatusType.ACTIVE,
            date_range=DateRange(valid_from=hire_date)
        )
        employee.add_status(initial_status)

        return employee

class ChangeEmployeeStatusService:
    """Domain service for changing employee status."""

    def change_status(
        self,
        employee: Employee,
        new_status_type: EmploymentStatusType,
        effective_date: date,
        reason: Optional[str] = None
    ) -> Employee:
        """Change employee status effective from a specific date."""
        # Close current status
        current_status = employee.get_status_at(date.today())
        if current_status:
            # Create a new status with updated valid_to
            closed_status = EmploymentStatus(
                status_type=current_status.status_type,
                date_range=DateRange(
                    valid_from=current_status.date_range.valid_from,
                    valid_to=effective_date
                ),
                reason=current_status.reason
            )
            # Replace the old status
            employee.statuses = [
                s for s in employee.statuses
                if s.date_range.valid_from != current_status.date_range.valid_from
            ]
            employee.statuses.append(closed_status)

        # Add new status
        new_status = EmploymentStatus(
            status_type=new_status_type,
            date_range=DateRange(valid_from=effective_date),
            reason=reason
        )
        employee.add_status(new_status)

        return employee
```

**`backend/app/domain/employee/events.py`:**
```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from app.domain.employee.value_objects import EmploymentStatusType

@dataclass
class EmployeeCreated:
    """Domain event: Employee was created."""
    employee_id: UUID
    email: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EmployeeUpdated:
    """Domain event: Employee was updated."""
    employee_id: UUID
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class EmployeeStatusChanged:
    """Domain event: Employee status changed."""
    employee_id: UUID
    old_status: EmploymentStatusType
    new_status: EmploymentStatusType
    effective_date: date
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

#### 2.2: Infrastructure Layer - Persistence

**`backend/app/infrastructure/persistence/models.py`:**
```python
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base
from app.domain.employee.value_objects import EmploymentStatusType

class EmployeeORM(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    hire_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    statuses = relationship("EmploymentStatusORM", back_populates="employee", cascade="all, delete-orphan")
    contracts = relationship("ContractORM", back_populates="employee")

class EmploymentStatusORM(Base):
    __tablename__ = "employment_statuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    status_type = Column(SQLEnum(EmploymentStatusType), nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employee = relationship("EmployeeORM", back_populates="statuses")
```

**`backend/app/infrastructure/persistence/employee_repository.py`:**
```python
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.domain.employee.models import Employee
from app.domain.employee.repository import EmployeeRepository
from app.domain.employee.value_objects import EmploymentStatus
from app.domain.shared.value_objects import DateRange
from app.infrastructure.persistence.models import EmployeeORM, EmploymentStatusORM

class SQLAlchemyEmployeeRepository(EmployeeRepository):
    """SQLAlchemy implementation of EmployeeRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: EmployeeORM) -> Employee:
        """Convert ORM model to domain entity."""
        statuses = [
            EmploymentStatus(
                status_type=s.status_type,
                date_range=DateRange(
                    valid_from=s.valid_from,
                    valid_to=s.valid_to
                ),
                reason=s.reason
            )
            for s in orm.statuses
        ]

        return Employee(
            id=orm.id,
            first_name=orm.first_name,
            last_name=orm.last_name,
            email=orm.email,
            phone=orm.phone,
            date_of_birth=orm.date_of_birth,
            hire_date=orm.hire_date,
            statuses=statuses,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    def _to_orm(self, employee: Employee) -> EmployeeORM:
        """Convert domain entity to ORM model."""
        orm = EmployeeORM(
            id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            phone=employee.phone,
            date_of_birth=employee.date_of_birth,
            hire_date=employee.hire_date,
        )

        orm.statuses = [
            EmploymentStatusORM(
                status_type=s.status_type,
                valid_from=s.date_range.valid_from,
                valid_to=s.date_range.valid_to,
                reason=s.reason
            )
            for s in employee.statuses
        ]

        return orm

    async def add(self, employee: Employee) -> Employee:
        orm = self._to_orm(employee)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_id(self, employee_id: UUID) -> Optional[Employee]:
        stmt = select(EmployeeORM).options(
            selectinload(EmployeeORM.statuses)
        ).where(EmployeeORM.id == employee_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_email(self, email: str) -> Optional[Employee]:
        stmt = select(EmployeeORM).options(
            selectinload(EmployeeORM.statuses)
        ).where(EmployeeORM.email == email)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        stmt = select(EmployeeORM).options(
            selectinload(EmployeeORM.statuses)
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def update(self, employee: Employee) -> Employee:
        # Delete existing statuses
        stmt = select(EmployeeORM).options(
            selectinload(EmployeeORM.statuses)
        ).where(EmployeeORM.id == employee.id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            raise ValueError(f"Employee {employee.id} not found")

        # Update fields
        orm.first_name = employee.first_name
        orm.last_name = employee.last_name
        orm.email = employee.email
        orm.phone = employee.phone
        orm.date_of_birth = employee.date_of_birth
        orm.hire_date = employee.hire_date

        # Replace statuses
        orm.statuses = [
            EmploymentStatusORM(
                status_type=s.status_type,
                valid_from=s.date_range.valid_from,
                valid_to=s.date_range.valid_to,
                reason=s.reason
            )
            for s in employee.statuses
        ]

        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def delete(self, employee_id: UUID) -> bool:
        stmt = select(EmployeeORM).where(EmployeeORM.id == employee_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return False

        await self.session.delete(orm)
        return True
```

#### 2.3: Application Layer - Commands & Queries

**`backend/app/application/employee/commands.py`:**
```python
from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID
from app.domain.employee.value_objects import EmploymentStatusType

@dataclass
class CreateEmployeeCommand:
    first_name: str
    last_name: str
    email: str
    hire_date: date
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None

@dataclass
class UpdateEmployeeCommand:
    employee_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None

@dataclass
class ChangeEmployeeStatusCommand:
    employee_id: UUID
    new_status: EmploymentStatusType
    effective_date: date
    reason: Optional[str] = None
```

**`backend/app/application/employee/queries.py`:**
```python
from dataclasses import dataclass
from uuid import UUID

@dataclass
class GetEmployeeQuery:
    employee_id: UUID

@dataclass
class ListEmployeesQuery:
    skip: int = 0
    limit: int = 100

@dataclass
class GetEmployeeByEmailQuery:
    email: str
```

**`backend/app/application/employee/handlers.py`:**
```python
from typing import List, Optional
from app.domain.employee.models import Employee
from app.domain.employee.repository import EmployeeRepository
from app.domain.employee.services import CreateEmployeeService, ChangeEmployeeStatusService
from app.application.employee.commands import (
    CreateEmployeeCommand,
    UpdateEmployeeCommand,
    ChangeEmployeeStatusCommand
)
from app.application.employee.queries import (
    GetEmployeeQuery,
    ListEmployeesQuery,
    GetEmployeeByEmailQuery
)

class CreateEmployeeHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository
        self.service = CreateEmployeeService()

    async def handle(self, command: CreateEmployeeCommand) -> Employee:
        # Check if email already exists
        existing = await self.repository.get_by_email(command.email)
        if existing:
            raise ValueError(f"Employee with email {command.email} already exists")

        # Create employee using domain service
        employee = self.service.create(
            first_name=command.first_name,
            last_name=command.last_name,
            email=command.email,
            hire_date=command.hire_date,
            phone=command.phone,
            date_of_birth=command.date_of_birth,
        )

        # Persist
        return await self.repository.add(employee)

class UpdateEmployeeHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def handle(self, command: UpdateEmployeeCommand) -> Employee:
        employee = await self.repository.get_by_id(command.employee_id)
        if not employee:
            raise ValueError(f"Employee {command.employee_id} not found")

        # Update fields
        if command.first_name:
            employee.first_name = command.first_name
        if command.last_name:
            employee.last_name = command.last_name
        if command.email:
            employee.email = command.email
        if command.phone:
            employee.phone = command.phone
        if command.date_of_birth:
            employee.date_of_birth = command.date_of_birth

        return await self.repository.update(employee)

class ChangeEmployeeStatusHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository
        self.service = ChangeEmployeeStatusService()

    async def handle(self, command: ChangeEmployeeStatusCommand) -> Employee:
        employee = await self.repository.get_by_id(command.employee_id)
        if not employee:
            raise ValueError(f"Employee {command.employee_id} not found")

        # Change status using domain service
        employee = self.service.change_status(
            employee=employee,
            new_status_type=command.new_status,
            effective_date=command.effective_date,
            reason=command.reason
        )

        return await self.repository.update(employee)

class GetEmployeeHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def handle(self, query: GetEmployeeQuery) -> Optional[Employee]:
        return await self.repository.get_by_id(query.employee_id)

class ListEmployeesHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def handle(self, query: ListEmployeesQuery) -> List[Employee]:
        return await self.repository.list(skip=query.skip, limit=query.limit)

class GetEmployeeByEmailHandler:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def handle(self, query: GetEmployeeByEmailQuery) -> Optional[Employee]:
        return await self.repository.get_by_email(query.email)
```

#### 2.4: API Layer - Endpoints

**`backend/app/api/v1/employees.py`:**
```python
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.domain.employee.value_objects import EmploymentStatusType
from app.infrastructure.persistence.employee_repository import SQLAlchemyEmployeeRepository
from app.application.employee.commands import (
    CreateEmployeeCommand,
    UpdateEmployeeCommand,
    ChangeEmployeeStatusCommand
)
from app.application.employee.queries import GetEmployeeQuery, ListEmployeesQuery
from app.application.employee.handlers import (
    CreateEmployeeHandler,
    UpdateEmployeeHandler,
    ChangeEmployeeStatusHandler,
    GetEmployeeHandler,
    ListEmployeesHandler
)

router = APIRouter()

# Pydantic schemas
class EmploymentStatusResponse(BaseModel):
    status_type: EmploymentStatusType
    valid_from: date
    valid_to: date | None
    reason: str | None

class EmployeeResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None
    date_of_birth: date | None
    hire_date: date | None
    statuses: List[EmploymentStatusResponse]

class CreateEmployeeRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    hire_date: date
    phone: str | None = None
    date_of_birth: date | None = None

class UpdateEmployeeRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    date_of_birth: date | None = None

class ChangeStatusRequest(BaseModel):
    new_status: EmploymentStatusType
    effective_date: date
    reason: str | None = None

# Helper function
def to_response(employee) -> EmployeeResponse:
    return EmployeeResponse(
        id=employee.id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        phone=employee.phone,
        date_of_birth=employee.date_of_birth,
        hire_date=employee.hire_date,
        statuses=[
            EmploymentStatusResponse(
                status_type=s.status_type,
                valid_from=s.date_range.valid_from,
                valid_to=s.date_range.valid_to,
                reason=s.reason
            )
            for s in employee.statuses
        ]
    )

# Endpoints
@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    request: CreateEmployeeRequest,
    db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyEmployeeRepository(db)
    handler = CreateEmployeeHandler(repository)

    command = CreateEmployeeCommand(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        hire_date=request.hire_date,
        phone=request.phone,
        date_of_birth=request.date_of_birth
    )

    try:
        employee = await handler.handle(command)
        await db.commit()
        return to_response(employee)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyEmployeeRepository(db)
    handler = GetEmployeeHandler(repository)

    query = GetEmployeeQuery(employee_id=employee_id)
    employee = await handler.handle(query)

    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    return to_response(employee)

@router.get("/", response_model=List[EmployeeResponse])
async def list_employees(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyEmployeeRepository(db)
    handler = ListEmployeesHandler(repository)

    query = ListEmployeesQuery(skip=skip, limit=limit)
    employees = await handler.handle(query)

    return [to_response(emp) for emp in employees]

@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    request: UpdateEmployeeRequest,
    db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyEmployeeRepository(db)
    handler = UpdateEmployeeHandler(repository)

    command = UpdateEmployeeCommand(
        employee_id=employee_id,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        phone=request.phone,
        date_of_birth=request.date_of_birth
    )

    try:
        employee = await handler.handle(command)
        await db.commit()
        return to_response(employee)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{employee_id}/status", response_model=EmployeeResponse)
async def change_employee_status(
    employee_id: UUID,
    request: ChangeStatusRequest,
    db: AsyncSession = Depends(get_db)
):
    repository = SQLAlchemyEmployeeRepository(db)
    handler = ChangeEmployeeStatusHandler(repository)

    command = ChangeEmployeeStatusCommand(
        employee_id=employee_id,
        new_status=request.new_status,
        effective_date=request.effective_date,
        reason=request.reason
    )

    try:
        employee = await handler.handle(command)
        await db.commit()
        return to_response(employee)
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

**Update `backend/app/api/v1/router.py`:**
```python
from fastapi import APIRouter
from app.api.v1 import employees

api_router = APIRouter()
api_router.include_router(employees.router, prefix="/employees", tags=["employees"])
```

#### 2.5: Database Migration

**Create migration:**
```bash
cd backend
alembic revision --autogenerate -m "create employees and employment_statuses tables"
alembic upgrade head
```

#### 2.6: Integration Tests

**`backend/tests/conftest.py`:**
```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from testcontainers.postgres import PostgresContainer
from app.database import Base
from app.main import app
from httpx import AsyncClient

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres

@pytest_asyncio.fixture
async def test_engine(postgres_container):
    database_url = postgres_container.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest_asyncio.fixture
async def test_session(test_engine):
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest_asyncio.fixture
async def client(test_session):
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

**`backend/tests/integration/test_employees.py`:**
```python
import pytest
from datetime import date
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_employee(client: AsyncClient):
    response = await client.post("/api/v1/employees/", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "hire_date": "2024-01-01",
        "phone": "+1234567890"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert len(data["statuses"]) == 1
    assert data["statuses"][0]["status_type"] == "active"

@pytest.mark.asyncio
async def test_get_employee(client: AsyncClient):
    # Create
    create_response = await client.post("/api/v1/employees/", json={
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "hire_date": "2024-01-01"
    })
    employee_id = create_response.json()["id"]

    # Get
    response = await client.get(f"/api/v1/employees/{employee_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "jane.smith@example.com"

@pytest.mark.asyncio
async def test_list_employees(client: AsyncClient):
    # Create multiple
    for i in range(3):
        await client.post("/api/v1/employees/", json={
            "first_name": f"Employee{i}",
            "last_name": "Test",
            "email": f"employee{i}@example.com",
            "hire_date": "2024-01-01"
        })

    # List
    response = await client.get("/api/v1/employees/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

@pytest.mark.asyncio
async def test_change_employee_status(client: AsyncClient):
    # Create
    create_response = await client.post("/api/v1/employees/", json={
        "first_name": "Status",
        "last_name": "Test",
        "email": "status.test@example.com",
        "hire_date": "2024-01-01"
    })
    employee_id = create_response.json()["id"]

    # Change status
    response = await client.post(f"/api/v1/employees/{employee_id}/status", json={
        "new_status": "on_leave",
        "effective_date": "2024-06-01",
        "reason": "Vacation"
    })

    assert response.status_code == 200
    data = response.json()
    assert len(data["statuses"]) == 2
```

---

## M3: Contract Context (Weeks 3-4)

### Objectives
- Implement Contract bounded context with cancellation & expiration
- Support multiple contract types
- Implement versioning (never overwrite contracts)
- Create scheduled job for auto-expiration
- Emit ContractExpired and ContractCanceled events to RabbitMQ
- Integration tests for all contract operations

### Backend Implementation

#### 3.1: RabbitMQ Infrastructure

**`backend/app/infrastructure/messaging/rabbitmq.py`:**
```python
import pika
from pika.adapters.blocking_connection import BlockingChannel
from app.config import get_settings

settings = get_settings()

def get_rabbitmq_connection():
    """Create RabbitMQ connection."""
    parameters = pika.URLParameters(settings.RABBITMQ_URL)
    return pika.BlockingConnection(parameters)

def get_channel() -> BlockingChannel:
    """Get RabbitMQ channel."""
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    # Declare exchanges
    channel.exchange_declare(
        exchange=settings.RABBITMQ_EXCHANGE_EMPLOYEE,
        exchange_type='topic',
        durable=True
    )
    channel.exchange_declare(
        exchange=settings.RABBITMQ_EXCHANGE_CONTRACT,
        exchange_type='topic',
        durable=True
    )

    return channel
```

**`backend/app/infrastructure/messaging/publisher.py`:**
```python
import json
from datetime import datetime
from dataclasses import asdict
from typing import Any
from app.infrastructure.messaging.rabbitmq import get_channel
from app.config import get_settings

settings = get_settings()

class EventPublisher:
    """Publishes domain events to RabbitMQ."""

    def __init__(self):
        self.channel = get_channel()

    def publish_contract_event(self, event: Any, routing_key: str):
        """Publish a contract event."""
        # Convert dataclass to dict
        if hasattr(event, '__dataclass_fields__'):
            event_dict = asdict(event)
        else:
            event_dict = event

        # Convert datetime objects to ISO format
        for key, value in event_dict.items():
            if isinstance(value, datetime):
                event_dict[key] = value.isoformat()
            elif isinstance(value, date):
                event_dict[key] = value.isoformat()

        message = json.dumps(event_dict)

        self.channel.basic_publish(
            exchange=settings.RABBITMQ_EXCHANGE_CONTRACT,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )

    def close(self):
        """Close the channel."""
        if self.channel:
            self.channel.close()
```

**`backend/app/infrastructure/messaging/schemas.py`:**
```python
from pydantic import BaseModel
from datetime import datetime, date
from uuid import UUID
from typing import Optional

class ContractExpiredEvent(BaseModel):
    """Event schema for contract expiration."""
    contract_id: UUID
    employee_id: UUID
    contract_type: str
    expiration_timestamp: datetime
    valid_from: date
    valid_to: date

class ContractCanceledEvent(BaseModel):
    """Event schema for contract cancellation."""
    contract_id: UUID
    employee_id: UUID
    contract_type: str
    cancellation_timestamp: datetime
    reason: Optional[str]
    canceled_by: str  # user ID or system
```

#### 3.2: Domain Layer - Contract

**`backend/app/domain/contract/value_objects.py`:**
```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ContractType(str, Enum):
    FIXED_MONTHLY = "fixed_monthly"
    HOURLY = "hourly"
    B2B_DAILY = "b2b_daily"
    B2B_HOURLY = "b2b_hourly"
    TASK_BASED = "task_based"
    COMMISSION_BASED = "commission_based"

class ContractStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"

@dataclass(frozen=True)
class CancellationInfo:
    """Value object for cancellation details."""
    canceled_at: datetime
    canceled_by: str
    reason: Optional[str] = None
```

**`backend/app/domain/contract/models.py`:**
```python
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4
from app.domain.contract.value_objects import (
    ContractType,
    ContractStatus,
    CancellationInfo
)
from app.domain.shared.value_objects import DateRange, Money

@dataclass
class Contract:
    """Contract aggregate root."""
    id: UUID = field(default_factory=uuid4)
    employee_id: UUID = None
    contract_type: ContractType = None
    status: ContractStatus = ContractStatus.ACTIVE
    rate: Money = None
    date_range: DateRange = None
    version: int = 1
    previous_version_id: Optional[UUID] = None
    cancellation_info: Optional[CancellationInfo] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def is_active(self) -> bool:
        """Check if contract is currently active."""
        return self.status == ContractStatus.ACTIVE

    def is_active_at(self, check_date: date) -> bool:
        """Check if contract is active at a specific date."""
        return self.is_active() and self.date_range.is_active_at(check_date)

    def can_be_expired(self) -> bool:
        """Check if contract can be expired."""
        return (
            self.status == ContractStatus.ACTIVE and
            self.date_range.valid_to and
            date.today() > self.date_range.valid_to
        )

    def expire(self) -> None:
        """Mark contract as expired."""
        if not self.can_be_expired():
            raise ValueError("Contract cannot be expired")
        self.status = ContractStatus.EXPIRED
        self.updated_at = datetime.utcnow()

    def cancel(self, canceled_by: str, reason: Optional[str] = None) -> None:
        """Cancel the contract."""
        if not self.is_active():
            raise ValueError("Only active contracts can be canceled")

        self.status = ContractStatus.CANCELED
        self.cancellation_info = CancellationInfo(
            canceled_at=datetime.utcnow(),
            canceled_by=canceled_by,
            reason=reason
        )
        self.updated_at = datetime.utcnow()
```

#### 3.3: Domain Services

**`backend/app/domain/contract/services.py`:**
```python
from uuid import UUID
from datetime import date
from decimal import Decimal
from typing import Optional
from app.domain.contract.models import Contract
from app.domain.contract.value_objects import ContractType
from app.domain.shared.value_objects import DateRange, Money

class CreateContractService:
    """Domain service for creating contracts."""

    def create(
        self,
        employee_id: UUID,
        contract_type: ContractType,
        rate_amount: Decimal,
        valid_from: date,
        valid_to: Optional[date] = None,
        currency: str = "USD"
    ) -> Contract:
        """Create a new contract."""
        return Contract(
            employee_id=employee_id,
            contract_type=contract_type,
            rate=Money(amount=rate_amount, currency=currency),
            date_range=DateRange(valid_from=valid_from, valid_to=valid_to),
            version=1
        )

class UpdateContractService:
    """Domain service for updating contracts (creates new version)."""

    def update(
        self,
        existing_contract: Contract,
        rate_amount: Optional[Decimal] = None,
        valid_from: Optional[date] = None,
        valid_to: Optional[date] = None,
        currency: Optional[str] = None
    ) -> Contract:
        """Create a new version of the contract."""
        # Close the existing contract
        if existing_contract.date_range.valid_to is None:
            # Set valid_to to the day before new contract starts
            if valid_from:
                from datetime import timedelta
                existing_contract.date_range = DateRange(
                    valid_from=existing_contract.date_range.valid_from,
                    valid_to=valid_from - timedelta(days=1)
                )

        # Create new contract version
        new_contract = Contract(
            employee_id=existing_contract.employee_id,
            contract_type=existing_contract.contract_type,
            rate=Money(
                amount=rate_amount if rate_amount else existing_contract.rate.amount,
                currency=currency if currency else existing_contract.rate.currency
            ),
            date_range=DateRange(
                valid_from=valid_from if valid_from else existing_contract.date_range.valid_from,
                valid_to=valid_to if valid_to is not None else existing_contract.date_range.valid_to
            ),
            version=existing_contract.version + 1,
            previous_version_id=existing_contract.id
        )

        return new_contract

class CancelContractService:
    """Domain service for canceling contracts."""

    def cancel(
        self,
        contract: Contract,
        canceled_by: str,
        reason: Optional[str] = None
    ) -> Contract:
        """Cancel a contract."""
        contract.cancel(canceled_by=canceled_by, reason=reason)
        return contract

class ExpireContractService:
    """Domain service for expiring contracts."""

    def expire(self, contract: Contract) -> Contract:
        """Expire a contract."""
        contract.expire()
        return contract

class ContractExpirationCheckerService:
    """Domain service for checking which contracts should be expired."""

    def should_expire(self, contract: Contract) -> bool:
        """Check if a contract should be expired."""
        return contract.can_be_expired()
```

#### 3.4: Domain Events

**`backend/app/domain/contract/events.py`:**
```python
from dataclasses import dataclass, field
from datetime import datetime, date
from uuid import UUID
from typing import Optional
from app.domain.contract.value_objects import ContractType

@dataclass
class ContractCreated:
    """Domain event: Contract was created."""
    contract_id: UUID
    employee_id: UUID
    contract_type: ContractType
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContractUpdated:
    """Domain event: Contract was updated (new version created)."""
    contract_id: UUID
    employee_id: UUID
    old_version: int
    new_version: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ContractCanceled:
    """Domain event: Contract was canceled."""
    contract_id: UUID
    employee_id: UUID
    contract_type: str
    cancellation_timestamp: datetime
    reason: Optional[str]
    canceled_by: str

@dataclass
class ContractExpired:
    """Domain event: Contract expired."""
    contract_id: UUID
    employee_id: UUID
    contract_type: str
    expiration_timestamp: datetime
    valid_from: date
    valid_to: date
```

_(Continue in next response due to length...)_

---

## Remaining Milestones Summary

**M4: Rates & Compensation (Week 5)**
- Rate entity with versioning
- Bonuses and commissions
- Rules tied to date ranges

**M5: Absence & Timesheet (Week 6)**
- Absence tracking with validation
- Timesheet entries
- Overtime calculation

**M6: Payroll Engine (Weeks 7-9)**
- PayrollRun entity
- Compensation calculation logic
- Handle backdated changes
- Payroll history

**M7: UI Implementation (Weeks 10-11)**
- React components for all entities
- Redux slices with RTK Query
- Forms and validation
- Reports UI

**M8: Integration & Testing (Weeks 12-13)**
- Event consumers for incoming events
- End-to-end testing
- Performance testing
- Documentation

---

## Testing Strategy

**Unit Tests:**
- Domain entities and value objects
- Domain services
- Business logic validation

**Integration Tests:**
- API endpoints
- Repository implementations
- Database queries
- Event publishing/consuming

**E2E Tests:**
- Complete user flows
- Contract lifecycle
- Payroll processing

**Performance Tests:**
- Payroll for 1k employees < 5s
- Database query optimization
- API response times

---

## Next Steps

1. Review this plan and confirm approach
2. Start with M1: Foundation
3. Implement incrementally, testing at each step
4. Create migration scripts as models are added
5. Document API as you build

Would you like me to continue with detailed implementation for M3 (Contract), M4, M5, M6, M7, and M8?
