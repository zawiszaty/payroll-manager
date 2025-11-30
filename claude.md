# Payroll Manager - Project Documentation

## Project Overview

A comprehensive payroll management system built with Domain-Driven Design (DDD) architecture, implementing multiple bounded contexts for employee management, contracts, compensation, absences, timesheets, payroll processing, and reporting.

## Technology Stack

### Backend
- **Python**: 3.14
- **Framework**: FastAPI
- **Database**: PostgreSQL (with asyncpg)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Message Queue**: RabbitMQ
- **Cache**: Redis
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: ruff, mypy

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Task Runner**: Taskfile

## Architecture

### DDD Modular Structure

Each bounded context (module) follows a complete DDD structure:

```
app/modules/{module_name}/
├── domain/              # Business logic, entities, value objects
│   ├── models.py       # Aggregate roots and entities
│   ├── value_objects.py # Immutable value objects
│   ├── repository.py   # Repository interface (abstract)
│   └── services.py     # Domain services
├── infrastructure/      # Technical implementations
│   ├── models.py       # ORM models
│   ├── repository.py   # Repository implementation
│   └── adapters.py     # ACL adapters for other module facades
├── application/         # Use cases (CQRS)
│   ├── commands.py     # Command definitions
│   ├── queries.py      # Query definitions
│   └── handlers.py     # Command/Query handlers
├── api/                 # Inter-module communication
│   └── facade.py       # Public API for other modules (ACL)
├── presentation/        # HTTP endpoints
│   ├── endpoints.py    # FastAPI routes
│   └── views.py        # Request/response models
└── tests/               # Module tests
    ├── conftest.py     # Test fixtures
    ├── test_domain.py  # Domain layer tests
    └── test_api.py     # API integration tests
```

### Key Design Patterns

1. **Domain-Driven Design (DDD)**
   - Bounded contexts for each business domain
   - Aggregate roots for consistency boundaries
   - Value objects for immutable concepts
   - Domain services for business logic

2. **CQRS (Command Query Responsibility Segregation)**
   - Separate commands (write) from queries (read)
   - Explicit command/query handlers
   - Clear separation of concerns

3. **Repository Pattern**
   - Abstract repository interfaces in domain layer
   - Concrete implementations in infrastructure layer
   - Dependency inversion principle

4. **Anti-Corruption Layer (ACL) Pattern**
   - Each module exposes a Facade in its `api/` layer
   - Other modules access it through Adapters in their `infrastructure/adapters.py`
   - Adapters translate between module boundaries
   - Prevents coupling between bounded contexts

5. **Dependency Injection**
   - FastAPI's dependency injection for database sessions
   - Repository injection into handlers
   - Facade injection into adapters

## Current Implementation Status

### ✅ M1: Foundation (Completed)
- Docker Compose setup with all services
- PostgreSQL database configuration
- Alembic migrations setup
- Core application structure
- Health check endpoints
- Auto-migration on startup via entrypoint.sh

### ✅ M2: Employee Module (Completed)

#### Domain Layer
- **Employee** aggregate root with:
  - Basic employee information (name, email, phone, dates)
  - Employment status history management
  - Status validation (no overlapping periods)
  - Query methods (get_status_at, is_active_at)

- **Value Objects**:
  - `EmploymentStatus`: Status with date range and reason
  - `EmploymentStatusType`: Enum (ACTIVE, ON_LEAVE, TERMINATED, SUSPENDED)
  - `DateRange`: Immutable date period with validation

- **Domain Services**:
  - `CreateEmployeeService`: Creates employee with initial ACTIVE status
  - `ChangeEmployeeStatusService`: Manages status transitions with proper date handling

#### Infrastructure Layer
- **ORM Models**: EmployeeORM, EmploymentStatusORM
- **Repository**: SQLAlchemyEmployeeRepository with async operations
- Proper relationship handling with cascade deletes
- Status update logic using explicit SQL deletes to avoid async issues

#### Application Layer (CQRS)
- **Commands**: CreateEmployee, UpdateEmployee, ChangeEmployeeStatus
- **Queries**: GetEmployee, ListEmployees, GetEmployeeByEmail
- **Handlers**: One handler per command/query with business validation

#### API Layer
- POST /api/v1/employees/ - Create employee (201)
- GET /api/v1/employees/ - List employees
- GET /api/v1/employees/{id} - Get single employee
- PUT /api/v1/employees/{id} - Update employee
- POST /api/v1/employees/{id}/status - Change employment status

#### Tests
- **Domain Tests** (5): Employee creation, status management, validation
- **API Tests** (6): CRUD operations, status changes, duplicate validation
- **Coverage**: 11/11 tests passing (100%)

### ✅ M3: Contract Module (Completed)

#### Domain Layer
- **Contract** aggregate root with:
  - Contract terms (type, rate, date range, hours, commission)
  - Status management (PENDING, ACTIVE, EXPIRED, CANCELED)
  - Activation, cancellation, and expiration logic
  - Query methods (is_active_at, is_expired_at)

- **Value Objects**:
  - `ContractTerms`: Immutable contract terms with validation
  - `ContractType`: Enum (FIXED_MONTHLY, HOURLY, B2B_DAILY, B2B_HOURLY, TASK_BASED, COMMISSION_BASED)
  - `ContractStatus`: Enum (ACTIVE, EXPIRED, CANCELED, PENDING)

- **Domain Services**:
  - `CreateContractService`: Creates contract with specified terms
  - `ActivateContractService`: Activates pending contracts
  - `CancelContractService`: Cancels active contracts with reason
  - `ExpireContractService`: Expires contracts that reached end date

#### Infrastructure Layer
- **ORM Model**: ContractORM with all contract fields
- **Repository**: SQLAlchemyContractRepository with async operations
- Support for multiple contract types with type-specific validation
- Employee-based contract querying

#### Application Layer (CQRS)
- **Commands**: CreateContract, ActivateContract, CancelContract, ExpireContract
- **Queries**: GetContract, GetContractsByEmployee, GetActiveContracts, ListContracts
- **Handlers**: One handler per command/query with business validation

#### API Layer
- POST /api/v1/contracts/ - Create contract (201)
- GET /api/v1/contracts/ - List all contracts
- GET /api/v1/contracts/{id} - Get single contract
- GET /api/v1/contracts/employee/{id} - Get contracts by employee
- GET /api/v1/contracts/employee/{id}/active - Get active contracts for employee
- POST /api/v1/contracts/{id}/activate - Activate contract
- POST /api/v1/contracts/{id}/cancel - Cancel contract
- POST /api/v1/contracts/{id}/expire - Expire contract

#### Tests
- **Domain Tests** (8): Contract creation, lifecycle, validation
- **API Tests** (6): CRUD operations, status changes, employee queries
- **Coverage**: 14/14 tests passing (100%)

### ✅ M4: Compensation Module (Completed)

#### Domain Layer
- **Rate** aggregate root with:
  - Rate type (BASE_SALARY, HOURLY_RATE, DAILY_RATE)
  - Amount as Money value object
  - Date range for validity period
  - Active status checking

- **Bonus** aggregate root with:
  - Bonus type (PERFORMANCE, ANNUAL, SIGNING, RETENTION, PROJECT, HOLIDAY)
  - Amount as Money value object
  - Payment date
  - Optional description

- **Deduction** aggregate root with:
  - Deduction type (TAX, INSURANCE, PENSION, LOAN, OTHER)
  - Amount as Money value object
  - Date range for validity period
  - Active status checking

- **Overtime** aggregate root with:
  - Overtime rule (multiplier, threshold_hours, date_range)
  - Calculate overtime pay based on hours worked
  - Validation (multiplier > 1.0, threshold > 0)

- **SickLeave** aggregate root with:
  - Sick leave rule (percentage, max_days, date_range)
  - Calculate sick pay based on monthly salary
  - Validation (percentage 0-100, max_days positive)
  - Support for unlimited sick days (max_days = None)

- **Value Objects**:
  - `RateType`: Enum for rate types
  - `BonusType`: Enum for bonus types
  - `DeductionType`: Enum for deduction types
  - `OvertimeRule`: Immutable overtime configuration
  - `SickLeaveRule`: Immutable sick leave configuration

#### Infrastructure Layer
- **ORM Models**: RateORM, BonusORM, DeductionORM, OvertimeORM, SickLeaveORM
- **Repositories**: 5 async repository implementations
- Indexed by employee_id for efficient queries
- Support for date-based queries (active rates, active deductions)

#### Application Layer (CQRS)
- **Commands**: CreateRate, CreateBonus, CreateDeduction, CreateOvertime, CreateSickLeave
- **Queries**: GetRate, GetRatesByEmployee, GetActiveRate, ListRates, GetBonus, GetBonusesByEmployee, ListBonuses, GetDeductionsByEmployee, GetActiveDeductions, GetOvertimeByEmployee, GetSickLeaveByEmployee
- **Handlers**: Complete handlers for all 5 compensation entities

#### API Layer
- POST /api/v1/compensation/rates/ - Create rate (201)
- GET /api/v1/compensation/rates/{id} - Get rate
- GET /api/v1/compensation/rates/ - List all rates
- GET /api/v1/compensation/rates/employee/{id} - Get rates by employee
- GET /api/v1/compensation/rates/employee/{id}/active - Get active rate
- POST /api/v1/compensation/bonuses/ - Create bonus (201)
- GET /api/v1/compensation/bonuses/{id} - Get bonus
- GET /api/v1/compensation/bonuses/ - List all bonuses
- GET /api/v1/compensation/bonuses/employee/{id} - Get bonuses by employee

#### Tests
- **Domain Tests** (10): Entity creation, rule validation, calculations
- **API Tests** (9): CRUD operations, employee queries, active rate retrieval
- **Coverage**: 19/19 tests passing (100%)

### Important Implementation Details

#### Status Period Management
When changing employee status, the system:
1. Closes the current status one day before the new status starts
2. Example: New status starts 2024-06-01, old status ends 2024-05-31
3. This prevents overlapping status periods

#### Repository Update Pattern
Due to SQLAlchemy async constraints, the update method:
1. Fetches the employee ORM object
2. Updates scalar fields directly
3. Uses explicit SQL DELETE for status records
4. Adds new status records
5. Flushes and refreshes to get updated data

This avoids `MissingGreenlet` errors from trying to manipulate relationship collections.

#### Sick Leave Calculation
Sick leave pay is calculated as:
- `monthly_salary * (percentage / 100) * days / 30`
- Caps at max_days if specified
- Supports unlimited sick days when max_days is None

## Project Structure

```
payroll-manager/
├── backend/
│   ├── app/
│   │   ├── modules/
│   │   │   ├── employee/           # ✅ Completed
│   │   │   ├── contract/           # ✅ Completed
│   │   │   ├── compensation/       # ✅ Completed
│   │   │   ├── absence/            # TODO
│   │   │   ├── timesheet/          # TODO
│   │   │   ├── payroll/            # TODO
│   │   │   └── reporting/          # TODO
│   │   ├── shared/
│   │   │   └── domain/
│   │   │       └── value_objects.py  # DateRange, Money
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── router.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── migrations/                  # Alembic migrations
│   ├── tests/                       # Legacy, being phased out
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── requirements.txt
├── docker-compose.yml
├── Taskfile.yml
├── project.md                        # Project specification
└── claude.md                         # This file

```

## Development Workflow

### Starting the Project

```bash
# Start all services
task up

# Or rebuild if needed
task rebuild

# Check status
task ps

# View logs
task logs
```

### Database Operations

```bash
# Create new migration
task migrate-create -- "description"

# Run migrations
task migrate

# Reset database (drops all data)
task reset-db

# Access database shell
task db-shell
```

### Testing

```bash
# Run all tests
task test

# Run specific module tests
task test-employee
task test-contract
task test-compensation

# Run with coverage
task test-coverage

# Watch mode
task test-watch
```

### Code Quality

```bash
# Lint code
task lint

# Auto-fix linting issues
task lint-fix

# Format code
task format

# Check formatting
task format-check

# Type checking
task type-check
```

### Other Commands

```bash
# Access backend shell
task shell

# Restart services
task restart

# Check health
task health

# Open API docs
task api-docs

# Show all tasks
task help
```

### ✅ M5: Absence Module (Completed)

#### Domain Layer
- **Absence** aggregate root:
  - Employee absence records with date ranges
  - Status management (pending, approved, rejected, cancelled)
  - Absence type classification (vacation, sick leave, parental, etc.)
  - Overlap detection with existing absences
  - Days calculation for the absence period

- **AbsenceBalance** aggregate root:
  - Annual leave balance tracking per employee
  - Balance by absence type and year
  - Days used/remaining calculation
  - Balance validation before approving absences

- **Value Objects**:
  - `AbsenceType`: VACATION, SICK_LEAVE, PARENTAL_LEAVE, UNPAID_LEAVE, BEREAVEMENT, STUDY_LEAVE, COMPASSIONATE
  - `AbsenceStatus`: PENDING, APPROVED, REJECTED, CANCELLED
  - `AbsenceBalanceInfo`: Balance snapshot with total, used, and remaining days

#### Infrastructure Layer
- **ORM Models**: AbsenceModel, AbsenceBalanceModel
- **Repositories**: SQLAlchemyAbsenceRepository, SQLAlchemyAbsenceBalanceRepository
- **Database Tables**: absences, absence_balances

#### Application Layer (CQRS)
- **Commands**:
  - CreateAbsenceCommand: Submit new absence request
  - ApproveAbsenceCommand: Approve absence and deduct from balance
  - RejectAbsenceCommand: Reject absence request
  - CancelAbsenceCommand: Cancel absence and return days to balance
  - CreateAbsenceBalanceCommand: Initialize employee leave balance
  - UpdateAbsenceBalanceCommand: Adjust total days for a balance

- **Queries**:
  - GetAbsenceQuery: Get absence by ID
  - ListAbsencesQuery: List all absences
  - GetAbsencesByEmployeeQuery: Get all absences for an employee
  - GetAbsencesByEmployeeAndStatusQuery: Filter absences by status
  - GetAbsenceBalanceQuery: Get balance by ID
  - ListAbsenceBalancesQuery: List all balances
  - GetAbsenceBalancesByEmployeeQuery: Get all balances for an employee
  - GetAbsenceBalancesByEmployeeAndYearQuery: Get balances for specific year

#### API Endpoints (14)
- POST `/api/v1/absence/absences/` - Create absence request
- GET `/api/v1/absence/absences/{id}` - Get absence
- GET `/api/v1/absence/absences/` - List all absences
- GET `/api/v1/absence/absences/employee/{id}` - Get absences by employee
- POST `/api/v1/absence/absences/{id}/approve` - Approve absence
- POST `/api/v1/absence/absences/{id}/reject` - Reject absence
- POST `/api/v1/absence/absences/{id}/cancel` - Cancel absence
- POST `/api/v1/absence/balances/` - Create absence balance
- GET `/api/v1/absence/balances/{id}` - Get balance with remaining days
- GET `/api/v1/absence/balances/` - List all balances
- GET `/api/v1/absence/balances/employee/{id}` - Get balances by employee
- GET `/api/v1/absence/balances/employee/{id}/year/{year}` - Get balances by year
- PATCH `/api/v1/absence/balances/{id}` - Update balance total days

#### Business Rules
- Absence requests start in PENDING status
- Only PENDING absences can be approved or rejected
- PENDING and APPROVED absences can be cancelled
- Approving an absence deducts days from the employee's balance
- Cancelling an APPROVED absence returns days to the balance
- Cannot create overlapping APPROVED absences for the same employee
- System validates sufficient balance before approving absence (if balance exists)

#### Tests
- Domain Tests (15): Entity creation, status transitions, balance operations, validation rules
- API Tests (14): CRUD operations, approval workflow, balance management, integration scenarios
- Coverage: 29/29 tests passing (100%)

#### Task Commands
```bash
task test-absence          # Run absence module tests
```

## Database Schema

### Current Schema

#### employees
- id (UUID, PK)
- first_name (VARCHAR 100)
- last_name (VARCHAR 100)
- email (VARCHAR 255, UNIQUE, INDEXED)
- phone (VARCHAR 20, nullable)
- date_of_birth (DATE, nullable)
- hire_date (DATE, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

#### employment_statuses
- id (UUID, PK)
- employee_id (UUID, FK -> employees.id)
- status_type (ENUM: active, on_leave, terminated, suspended)
- valid_from (DATE)
- valid_to (DATE, nullable)
- reason (VARCHAR 500, nullable)
- created_at (TIMESTAMP)

#### contracts
- id (UUID, PK)
- employee_id (UUID, INDEXED)
- contract_type (ENUM: fixed_monthly, hourly, b2b_daily, b2b_hourly, task_based, commission_based)
- status (ENUM: active, expired, canceled, pending)
- version (INTEGER)
- rate_amount (NUMERIC 12,2)
- rate_currency (VARCHAR 3)
- valid_from (DATE)
- valid_to (DATE, nullable)
- hours_per_week (INTEGER, nullable)
- commission_percentage (NUMERIC 5,2, nullable)
- description (TEXT, nullable)
- cancellation_reason (VARCHAR 500, nullable)
- canceled_at (DATE, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

#### rates
- id (UUID, PK)
- employee_id (UUID, INDEXED)
- rate_type (ENUM: base_salary, hourly_rate, daily_rate)
- amount (NUMERIC 12,2)
- currency (VARCHAR 3)
- valid_from (DATE)
- valid_to (DATE, nullable)
- description (VARCHAR 500, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

#### bonuses
- id (UUID, PK)
- employee_id (UUID, INDEXED)
- bonus_type (ENUM: performance, annual, signing, retention, project, holiday)
- amount (NUMERIC 12,2)
- currency (VARCHAR 3)
- payment_date (DATE)
- description (VARCHAR 500, nullable)
- created_at (TIMESTAMP)

#### deductions
- id (UUID, PK)
- employee_id (UUID, INDEXED)
- deduction_type (ENUM: tax, insurance, pension, loan, other)
- amount (NUMERIC 12,2)
- currency (VARCHAR 3)
- valid_from (DATE)
- valid_to (DATE, nullable)
- description (VARCHAR 500, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

#### overtime_rules
- id (UUID, PK)
- employee_id (UUID, INDEXED)
- multiplier (NUMERIC 5,2)
- threshold_hours (INTEGER)
- valid_from (DATE)
- valid_to (DATE, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

#### sick_leave_rules
- id (UUID, PK)
- employee_id (UUID, INDEXED)
- percentage (NUMERIC 5,2)
- max_days (INTEGER, nullable)
- valid_from (DATE)
- valid_to (DATE, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

## Configuration

### Environment Variables (.env)

```env
DATABASE_URL=postgresql://payroll_user:payroll_pass@postgres:5432/payroll_db
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-change-in-production
```

### Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Coding Standards

### General Rules
- **No comments in code** - code should be self-explanatory
- Use clear, descriptive names for variables and functions
- Follow Python PEP 8 style guide
- Use type hints for all function signatures
- Keep functions small and focused

### Testing Rules
- Tests must be located in `app/modules/{module}/tests/`
- Use descriptive test names: `test_what_it_does`
- Cover both happy paths and error cases
- Use fixtures from conftest.py for common setup
- Tests should be independent and isolated

### DDD Rules
- Domain layer should not depend on infrastructure
- Use value objects for immutable concepts
- Aggregate roots enforce consistency boundaries
- Domain services for operations spanning multiple entities
- Repository interfaces in domain, implementations in infrastructure

## Next Steps (Roadmap)

### M5: Absence Module (TODO)
- Leave types (vacation, sick, unpaid)
- Leave balances
- Absence requests and approvals
- Absence history

### M6: Timesheet Module (TODO)
- Time entries
- Overtime tracking
- Approval workflows
- Project/task allocation

### M7: Payroll Processing (TODO)
- Payroll calculation engine
- Pay slip generation
- Payment processing
- Tax calculations
- Payroll runs history

### M8: Reporting Module (TODO)
- Payroll reports
- Employee reports
- Tax reports
- Custom report builder
- Export functionality

## Troubleshooting

### Common Issues

#### Tests failing with MissingGreenlet error
**Solution**: Use explicit SQL operations instead of manipulating ORM relationship collections directly. See repository update method in employee module.

#### Migration conflicts
**Solution**: Reset database with `task reset-db`

#### Permission denied on files
**Solution**: Some files are created by Docker with root ownership. Remove them from within the container:
```bash
docker compose exec backend rm -rf path/to/file
```

#### Port already in use
**Solution**: Stop conflicting services or change ports in docker-compose.yml

### Debug Mode

To enable SQL query logging, set `echo=True` in database.py engine configuration.

## How to Create a New Module

### Step-by-Step Guide

Follow this systematic approach when creating a new module in the payroll manager system:

#### 1. Create Module Structure

Create the following directory structure under `backend/app/modules/{module_name}/`:

```bash
backend/app/modules/{module_name}/
├── domain/
│   ├── __init__.py
│   ├── models.py           # Aggregate roots and entities
│   ├── value_objects.py    # Immutable value objects
│   ├── repository.py       # Repository interface (abstract)
│   └── services.py         # Domain services
├── infrastructure/
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy ORM models
│   ├── repository.py       # Repository implementation
│   ├── read_model.py       # Read-side models for queries
│   └── adapters.py         # ACL adapters for other module facades
├── application/
│   ├── __init__.py
│   ├── commands.py         # Command definitions (write operations)
│   ├── queries.py          # Query definitions (read operations)
│   └── handlers.py         # Command and query handlers
├── api/
│   ├── __init__.py
│   └── facade.py           # Public facade for inter-module communication
├── presentation/
│   ├── __init__.py
│   ├── endpoints.py        # FastAPI routes
│   └── views.py            # Request/response models (Pydantic)
└── tests/
    ├── __init__.py
    ├── conftest.py         # Test fixtures
    ├── test_domain.py      # Domain layer tests
    ├── test_api.py         # API integration tests
    └── test_facade.py      # Facade integration tests
```

#### 2. Domain Layer (Start Here)

**a. Define Value Objects** (`domain/value_objects.py`)
- Create immutable value objects for concepts without identity
- Use `@dataclass(frozen=True)` for immutability
- Add validation in `__post_init__`
- Examples: Status enums, DateRange, Money, Rules

**b. Define Aggregate Roots** (`domain/models.py`)
- Create main entities with identity (UUID)
- Implement business logic as methods
- Ensure invariants are always maintained
- Use value objects for complex attributes
- Keep entities free from infrastructure concerns

**c. Define Repository Interface** (`domain/repository.py`)
- Create abstract base class using `ABC`
- Define async methods for data access
- Use domain entities as return types
- Keep interface focused on business needs

**d. Define Domain Services** (`domain/services.py`)
- Create services for operations spanning multiple entities
- Implement complex business rules
- Keep services stateless
- Use dependency injection for repositories

#### 3. Infrastructure Layer

**a. Create ORM Models** (`infrastructure/models.py`)
- Define SQLAlchemy models with `declarative_base()`
- Map to database tables
- Define relationships and constraints
- Use proper column types and indexes

**b. Implement Repository** (`infrastructure/repository.py`)
- Implement the domain repository interface
- Convert between ORM models and domain entities
- Use async/await for all database operations
- Handle relationship loading carefully (avoid MissingGreenlet errors)

**c. Create Read Models** (`infrastructure/read_model.py`)
- Define lightweight models for query operations
- Use for list views and reporting
- Separate from write-side entities

#### 4. Application Layer (CQRS)

**a. Define Commands** (`application/commands.py`)
- Create dataclasses for write operations
- Include all required data for the operation
- One command per business action

**b. Define Queries** (`application/queries.py`)
- Create dataclasses for read operations
- Include filter criteria and pagination
- One query per data retrieval need

**c. Implement Handlers** (`application/handlers.py`)
- One handler per command/query
- Handlers orchestrate domain services and repositories
- Implement validation and error handling
- Use async/await for database operations

#### 5. API Layer (Inter-Module Communication)

**a. Define Facade Interface** (`api/facade.py`)
- **IMPORTANT**: Every facade MUST have an abstract interface (ABC)
- Create a facade interface defining the public API contract
- Implement the interface in a concrete facade class
- Define methods for operations other modules can use
- Use DTOs (Data Transfer Objects) for data exchange
- Keep facade interface stable and versioned
- This is the **only** entry point for other modules

**Example:**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID
from datetime import date

@dataclass
class EmployeeDTO:
    id: UUID
    first_name: str
    last_name: str
    email: str

class IEmployeeFacade(ABC):
    @abstractmethod
    async def get_employee(self, employee_id: UUID) -> EmployeeDTO | None:
        pass

    @abstractmethod
    async def is_employee_active(self, employee_id: UUID, date: date) -> bool:
        pass

class EmployeeFacade(IEmployeeFacade):
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def get_employee(self, employee_id: UUID) -> EmployeeDTO | None:
        employee = await self.repository.get_by_id(employee_id)
        if not employee:
            return None
        return EmployeeDTO(
            id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email
        )

    async def is_employee_active(self, employee_id: UUID, date: date) -> bool:
        employee = await self.repository.get_by_id(employee_id)
        return employee.is_active_at(date) if employee else False
```

#### 6. Infrastructure - ACL Adapters

**a. Create Adapters** (`infrastructure/adapters.py`)
- **IMPORTANT**: Every adapter MUST have an abstract interface (ABC)
- When Module B needs data from Module A, create an adapter in Module B
- Adapter uses Module A's facade **interface** (not concrete implementation)
- Adapter translates between Module A's DTOs and Module B's needs
- This is the **Anti-Corruption Layer (ACL)**
- Using interfaces enables mocking in tests without touching real module data

**Example (in Contract module using Employee facade):**
```python
from abc import ABC, abstractmethod
from app.modules.employee.api.facade import IEmployeeFacade, EmployeeDTO
from uuid import UUID
from datetime import date

class IEmployeeAdapter(ABC):
    @abstractmethod
    async def validate_employee_exists(self, employee_id: UUID) -> bool:
        pass

    @abstractmethod
    async def validate_employee_active(self, employee_id: UUID, date: date) -> bool:
        pass

class EmployeeAdapter(IEmployeeAdapter):
    def __init__(self, employee_facade: IEmployeeFacade):
        self.employee_facade = employee_facade

    async def validate_employee_exists(self, employee_id: UUID) -> bool:
        employee = await self.employee_facade.get_employee(employee_id)
        return employee is not None

    async def validate_employee_active(self, employee_id: UUID, date: date) -> bool:
        return await self.employee_facade.is_employee_active(employee_id, date)
```

**Key Points for Facades and Adapters:**
- ✅ **Every facade MUST have an interface (ABC)** - enables mocking and loose coupling
- ✅ **Every adapter MUST have an interface (ABC)** - enables test isolation
- ✅ **Adapters depend on facade interfaces, not concrete implementations**
- ✅ **In tests, ALWAYS mock adapters** - prevents cross-module data contamination
- ✅ **Example**: Module C uses Module A and B → Module C has adapters for A and B → Module C tests mock both adapters

#### 7. Presentation Layer (HTTP API)

**a. Define Views** (`presentation/views.py`)
- Create Pydantic models for request/response
- Use proper validation
- Define separate models for create, update, and response
- Follow REST conventions

**b. Implement Endpoints** (`presentation/endpoints.py`)
- Create FastAPI router
- Define RESTful routes
- Use dependency injection for database sessions
- Call appropriate handlers
- Return proper HTTP status codes
- Handle exceptions gracefully

#### 8. Write Tests

**a. Domain Tests** (`tests/test_domain.py`)
- Test entity creation and validation
- Test business logic in domain services
- Test value object validation
- Test edge cases and error conditions
- Keep tests independent and isolated

**b. API Tests** (`tests/test_api.py`)
- Test all endpoints (happy paths)
- Test error cases (validation, not found, etc.)
- Test integration between layers
- Use fixtures for test data setup

**c. Test Fixtures** (`tests/conftest.py`)
- Create reusable fixtures for database sessions
- Create fixtures for test data
- Use `pytest.mark.asyncio` for async tests

**d. Facade Tests** (`tests/test_facade.py`)
- Test facade operations
- Test DTO conversions
- Test inter-module contracts
- Mock dependencies when needed

**e. Testing with Mocked Adapters** (`tests/test_*.py`)
- **CRITICAL**: When Module C uses Module A and Module B through adapters, ALWAYS mock the adapters in Module C's tests
- This prevents tests from interacting with real data from other modules
- Use adapter interfaces to create mock implementations
- Each module's tests should be completely isolated from other modules
- Example: If Contract module uses EmployeeAdapter, mock IEmployeeAdapter in contract tests

**Example (mocking adapter in tests):**
```python
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import date

from app.modules.contract.infrastructure.adapters import IEmployeeAdapter
from app.modules.contract.application.handlers import CreateContractHandler

class MockEmployeeAdapter(IEmployeeAdapter):
    async def validate_employee_exists(self, employee_id: UUID) -> bool:
        return True  # Mock: always return True for tests

    async def validate_employee_active(self, employee_id: UUID, date: date) -> bool:
        return True  # Mock: always return True for tests

@pytest.mark.asyncio
async def test_create_contract_with_mocked_employee(db_session):
    # Use mocked adapter instead of real one
    mock_employee_adapter = MockEmployeeAdapter()
    repository = SQLAlchemyContractRepository(db_session)
    handler = CreateContractHandler(repository, mock_employee_adapter)

    # Test contract creation without touching Employee module data
    command = CreateContractCommand(
        employee_id=uuid4(),
        contract_type="fixed_monthly",
        # ... other fields
    )

    contract = await handler.handle(command)
    assert contract.id is not None
```

#### 9. Database Migration

**a. Create Migration**
```bash
task migrate-create -- "add_{module_name}_tables"
```

**b. Review and Edit Migration**
- Check auto-generated migration
- Add missing indexes
- Add constraints
- Test upgrade and downgrade

**c. Run Migration**
```bash
task migrate
```

#### 10. Register Module

**a. Add to API Router** (`backend/app/api/v1/router.py`)
```python
from app.modules.{module_name}.presentation.endpoints import router as {module_name}_router

api_router.include_router(
    {module_name}_router,
    prefix="/{module_name}",
    tags=["{module_name}"]
)
```

**b. Add Task Commands** (`Taskfile.yml`)
```yaml
test-{module_name}:
  desc: Run {module_name} module tests
  cmds:
    - docker compose exec backend pytest app/modules/{module_name}/tests/ -v
```

#### 11. Update Documentation

- Update this `claude.md` file with:
  - Module status (✅ or TODO)
  - Domain layer details
  - Infrastructure details
  - Application layer (CQRS)
  - API endpoints
  - Business rules
  - Tests coverage
  - Database schema

### Inter-Module Communication Pattern

The system uses the **Anti-Corruption Layer (ACL)** pattern to maintain clean boundaries between bounded contexts. This ensures modules remain independent and can evolve separately.

#### Architecture Overview

```
Module A                           Module B
┌─────────────────────┐           ┌─────────────────────┐
│ Domain              │           │ Domain              │
│ Application         │           │ Application         │
│                     │           │                     │
│ API Layer           │           │ Infrastructure      │
│ ┌─────────────────┐ │           │ ┌─────────────────┐ │
│ │ ModuleAFacade   │◄├───────────┤─│ ModuleAAdapter  │ │
│ │ (Public API)    │ │           │ │ (ACL)           │ │
│ └─────────────────┘ │           │ └─────────────────┘ │
│                     │           │                     │
│ Presentation        │           │ Presentation        │
└─────────────────────┘           └─────────────────────┘
```

#### How It Works

1. **Module A exposes a Facade** (`app/modules/module_a/api/facade.py`)
   - Defines DTOs for data exchange
   - Exposes only necessary operations
   - Hides internal implementation details
   - Provides stable, versioned interface

2. **Module B creates an Adapter** (`app/modules/module_b/infrastructure/adapters.py`)
   - Uses Module A's facade
   - Translates DTOs to Module B's domain concepts
   - Provides Module B-specific interface
   - Acts as Anti-Corruption Layer

#### Rules for Inter-Module Communication

1. **NEVER access another module's:**
   - Database tables directly
   - Repository implementations
   - Domain entities
   - Application handlers
   - Internal services

2. **ALWAYS communicate through:**
   - Facades (api/facade.py) as the public interface
   - Adapters (infrastructure/adapters.py) as the consumer
   - DTOs for data transfer

3. **Facade Design Guidelines:**
   - Return DTOs, not domain entities
   - Keep interface minimal and focused
   - Version breaking changes
   - Don't expose internal state

4. **Adapter Design Guidelines:**
   - Located in the consuming module's infrastructure
   - Translates external DTOs to internal concepts
   - Handles errors from external module
   - Can combine multiple facade calls

#### Example: Contract Module Using Employee Module

**Module A: Employee Facade** (`app/modules/employee/api/facade.py`)
```python
from dataclasses import dataclass
from uuid import UUID
from datetime import date

@dataclass
class EmployeeDTO:
    id: UUID
    first_name: str
    last_name: str
    email: str
    is_active: bool

class EmployeeFacade:
    def __init__(self, repository: EmployeeRepository):
        self.repository = repository

    async def get_employee(self, employee_id: UUID) -> EmployeeDTO | None:
        employee = await self.repository.get_by_id(employee_id)
        if not employee:
            return None
        return EmployeeDTO(
            id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            is_active=employee.is_active_at(date.today())
        )

    async def is_employee_active(self, employee_id: UUID, check_date: date) -> bool:
        employee = await self.repository.get_by_id(employee_id)
        return employee.is_active_at(check_date) if employee else False
```

**Module B: Employee Adapter** (`app/modules/contract/infrastructure/adapters.py`)
```python
from app.modules.employee.api.facade import EmployeeFacade
from uuid import UUID
from datetime import date

class EmployeeAdapter:
    def __init__(self, employee_facade: EmployeeFacade):
        self.employee_facade = employee_facade

    async def validate_employee_exists(self, employee_id: UUID) -> None:
        employee = await self.employee_facade.get_employee(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")

    async def validate_employee_active_for_contract(
        self,
        employee_id: UUID,
        contract_start_date: date
    ) -> None:
        is_active = await self.employee_facade.is_employee_active(
            employee_id,
            contract_start_date
        )
        if not is_active:
            raise ValueError(
                f"Employee {employee_id} is not active on {contract_start_date}"
            )
```

**Using the Adapter in Contract Handler** (`app/modules/contract/application/handlers.py`)
```python
class CreateContractHandler:
    def __init__(
        self,
        contract_repository: ContractRepository,
        employee_adapter: EmployeeAdapter
    ):
        self.contract_repository = contract_repository
        self.employee_adapter = employee_adapter

    async def handle(self, command: CreateContractCommand) -> Contract:
        # Validate employee exists and is active
        await self.employee_adapter.validate_employee_exists(command.employee_id)
        await self.employee_adapter.validate_employee_active_for_contract(
            command.employee_id,
            command.valid_from
        )

        # Create contract
        contract = Contract(...)
        return await self.contract_repository.save(contract)
```

#### Benefits of This Pattern

1. **Loose Coupling**: Modules don't know about each other's internals
2. **Independent Evolution**: Can change module internals without affecting others
3. **Clear Boundaries**: Explicit about what's public vs private
4. **Testability**: Easy to mock facades in tests
5. **Domain Protection**: External concepts don't pollute your domain

### Module Development Principles

#### Domain-Driven Design Principles

1. **Ubiquitous Language**
   - Use business terminology consistently
   - Same terms in code, docs, and conversations
   - Avoid technical jargon in domain layer

2. **Bounded Context Isolation**
   - Each module is a bounded context
   - Modules communicate ONLY through facades (api/facade.py)
   - NEVER access another module's database, repository, or domain objects directly
   - Use ACL adapters in infrastructure for external module dependencies

3. **Aggregate Boundaries**
   - One aggregate root per consistency boundary
   - Changes to aggregate happen through aggregate root
   - Use IDs to reference other aggregates

4. **Value Objects Over Primitives**
   - Use value objects instead of primitive types
   - Encapsulate validation in value objects
   - Make value objects immutable

5. **Domain Services for Complex Logic**
   - Use when logic spans multiple entities
   - Keep services stateless
   - Services use repository interfaces

#### CQRS Principles

1. **Separate Reads from Writes**
   - Commands change state, return minimal data
   - Queries read state, never modify
   - Use different models for read and write if needed

2. **One Handler Per Operation**
   - Single Responsibility Principle
   - Clear, focused handlers
   - Easy to test and maintain

3. **Explicit Operations**
   - Commands represent user intent
   - Clear naming: CreateEmployee, ApproveAbsence
   - Include all necessary data in command

#### Repository Pattern Principles

1. **Interface in Domain, Implementation in Infrastructure**
   - Domain defines what it needs
   - Infrastructure provides implementation
   - Dependency inversion principle

2. **Domain Entities In, Domain Entities Out**
   - Repository works with domain entities
   - ORM conversion happens inside repository
   - Keep domain layer pure

3. **Async All The Way**
   - Use async/await for all database operations
   - Avoid blocking calls
   - Be careful with relationship loading

#### Testing Principles

1. **Co-locate Tests with Code**
   - Tests live in module's tests/ directory
   - Easy to find and maintain
   - Module ownership of test quality

2. **Independent and Isolated**
   - Each test can run alone
   - No shared state between tests
   - Use fixtures for setup

3. **Test Behavior, Not Implementation**
   - Focus on what, not how
   - Test business rules
   - Avoid testing framework code

4. **Coverage Targets**
   - 100% test coverage goal
   - Test happy paths and error cases
   - Test edge cases and validation

5. **Mock External Dependencies**
   - **CRITICAL**: Always mock adapters in module tests
   - Use adapter interfaces (ABC) to create mocks
   - Example: Module C tests should mock adapters for modules A and B
   - This ensures tests don't interact with real data from other modules
   - Tests should be completely isolated per module

#### Code Quality Principles

1. **No Comments in Code**
   - Code should be self-documenting
   - Use clear, descriptive names
   - Refactor complex code instead of commenting

2. **Type Hints Everywhere**
   - All function signatures have types
   - Helps catch errors early
   - Serves as documentation

3. **Keep Functions Small**
   - One purpose per function
   - Easy to understand and test
   - Extract complex logic to helpers

4. **Error Handling**
   - Validate at boundaries (API, domain services)
   - Use specific exceptions
   - Let exceptions propagate with context

#### Anti-Corruption Layer (ACL) Principles

1. **Facade as Public Contract**
   - Each module exposes one facade in api/facade.py
   - Facade is the ONLY way other modules can access functionality
   - Use DTOs for all data exchange
   - Never expose domain entities directly

2. **Adapter as Translation Layer**
   - Consumer module creates adapter in infrastructure/adapters.py
   - Adapter translates external DTOs to internal concepts
   - Adapter provides module-specific interface
   - Multiple adapters can use the same facade

3. **Strict Isolation**
   - No direct database access across modules
   - No direct repository access across modules
   - No sharing of domain entities between modules
   - Communication only through facade → adapter

4. **Versioning and Stability**
   - Keep facade interface stable
   - Version breaking changes explicitly
   - Deprecate old methods before removing
   - Document facade contracts clearly

#### Database Principles

1. **Migrations for All Changes**
   - Never modify database manually
   - All changes through Alembic migrations
   - Test upgrade and downgrade

2. **Proper Indexing**
   - Index foreign keys
   - Index frequently queried columns
   - Consider query patterns

3. **Avoid N+1 Queries**
   - Use eager loading when needed
   - Be mindful of relationship loading
   - Use read models for complex queries

4. **Handle Async Carefully**
   - Watch for MissingGreenlet errors
   - Use explicit queries for updates
   - Refresh objects after flush when needed

### Common Patterns and Examples

#### Creating an Aggregate Root

```python
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import date

@dataclass
class MyEntity:
    id: UUID = field(default_factory=uuid4)
    name: str
    status: MyStatus
    created_at: date = field(default_factory=date.today)

    def change_status(self, new_status: MyStatus) -> None:
        self._validate_status_transition(new_status)
        self.status = new_status

    def _validate_status_transition(self, new_status: MyStatus) -> None:
        # Business validation logic
        pass
```

#### Creating a Value Object

```python
from dataclasses import dataclass
from enum import Enum

class MyStatusType(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"

@dataclass(frozen=True)
class MyStatus:
    status_type: MyStatusType
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.status_type == MyStatusType.CLOSED and not self.reason:
            raise ValueError("Closed status requires a reason")
```

#### Creating a Repository Interface

```python
from abc import ABC, abstractmethod
from uuid import UUID

class MyEntityRepository(ABC):
    @abstractmethod
    async def save(self, entity: MyEntity) -> MyEntity:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> MyEntity | None:
        pass

    @abstractmethod
    async def list_all(self) -> list[MyEntity]:
        pass
```

#### Creating a Command Handler

```python
from dataclasses import dataclass
from uuid import UUID

@dataclass
class CreateMyEntityCommand:
    name: str
    status_type: str

class CreateMyEntityHandler:
    def __init__(self, repository: MyEntityRepository):
        self.repository = repository

    async def handle(self, command: CreateMyEntityCommand) -> MyEntity:
        status = MyStatus(
            status_type=MyStatusType(command.status_type)
        )
        entity = MyEntity(
            name=command.name,
            status=status
        )
        return await self.repository.save(entity)
```

#### Creating API Endpoints (Presentation Layer)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/", response_model=MyEntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    request: CreateMyEntityRequest,
    db: AsyncSession = Depends(get_db)
) -> MyEntityResponse:
    repository = SQLAlchemyMyEntityRepository(db)
    handler = CreateMyEntityHandler(repository)

    command = CreateMyEntityCommand(
        name=request.name,
        status_type=request.status_type
    )

    entity = await handler.handle(command)
    return MyEntityResponse.from_entity(entity)
```

#### Creating a Facade (API Layer)

```python
from dataclasses import dataclass
from uuid import UUID
from datetime import date

@dataclass
class MyEntityDTO:
    id: UUID
    name: str
    status: str

class MyModuleFacade:
    def __init__(self, repository: MyEntityRepository):
        self.repository = repository

    async def get_entity(self, entity_id: UUID) -> MyEntityDTO | None:
        entity = await self.repository.get_by_id(entity_id)
        if not entity:
            return None
        return MyEntityDTO(
            id=entity.id,
            name=entity.name,
            status=entity.status.status_type.value
        )

    async def validate_entity_exists(self, entity_id: UUID) -> bool:
        entity = await self.repository.get_by_id(entity_id)
        return entity is not None
```

#### Creating an ACL Adapter (Infrastructure Layer)

```python
from app.modules.my_module.api.facade import MyModuleFacade, MyEntityDTO
from uuid import UUID

class MyModuleAdapter:
    def __init__(self, facade: MyModuleFacade):
        self.facade = facade

    async def get_entity_name(self, entity_id: UUID) -> str | None:
        dto = await self.facade.get_entity(entity_id)
        return dto.name if dto else None

    async def ensure_entity_exists(self, entity_id: UUID) -> None:
        if not await self.facade.validate_entity_exists(entity_id):
            raise ValueError(f"Entity {entity_id} does not exist")
```

### Checklist for New Module

Use this checklist to ensure completeness:

- [ ] Domain layer complete
  - [ ] Value objects defined
  - [ ] Aggregate roots defined
  - [ ] Repository interface defined
  - [ ] Domain services implemented
- [ ] Infrastructure layer complete
  - [ ] ORM models created
  - [ ] Repository implemented
  - [ ] Read models created (if needed)
  - [ ] ACL adapter interfaces (ABC) created (if module depends on other modules)
  - [ ] ACL adapter implementations created (if module depends on other modules)
- [ ] Application layer complete
  - [ ] Commands defined
  - [ ] Queries defined
  - [ ] Handlers implemented
- [ ] API layer complete (Inter-module communication)
  - [ ] Facade interface (ABC) defined
  - [ ] Facade implementation created with DTOs
  - [ ] Public methods defined
  - [ ] Facade interface stable
- [ ] Presentation layer complete (HTTP API)
  - [ ] Request/response views defined
  - [ ] Endpoints implemented
  - [ ] Proper status codes used
- [ ] Tests complete
  - [ ] Domain tests written
  - [ ] API tests written
  - [ ] Facade tests written
  - [ ] Adapter mocks created for cross-module dependencies
  - [ ] Tests use mocked adapters (no real data from other modules)
  - [ ] All tests passing
  - [ ] 100% coverage achieved
- [ ] Database migration complete
  - [ ] Migration created
  - [ ] Migration tested
  - [ ] Indexes added
- [ ] Integration complete
  - [ ] Module registered in API router
  - [ ] Task commands added
  - [ ] Documentation updated

## Contributing Guidelines

When adding a new module, follow the step-by-step guide above and ensure all checklist items are completed.

## Important Files

- `project.md` - Original project specification
- `claude.md` - This documentation (for AI context)
- `Taskfile.yml` - Development commands
- `docker-compose.yml` - Service orchestration
- `backend/app/main.py` - Application entry point
- `backend/app/database.py` - Database configuration
- `backend/migrations/env.py` - Migration configuration

## Notes for Future Development

- All modules should follow the employee module structure
- Tests must be co-located with module code
- Use shared value objects (DateRange, Money) when appropriate
- Keep domain logic pure - no framework dependencies
- Always use async/await for database operations
- Validate business rules in domain services, not endpoints
- Use explicit status codes in API responses
- Document complex business logic in docstrings
