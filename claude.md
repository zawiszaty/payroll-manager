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
│   └── repository.py   # Repository implementation
├── application/         # Use cases (CQRS)
│   ├── commands.py     # Command definitions
│   ├── queries.py      # Query definitions
│   └── handlers.py     # Command/Query handlers
├── api/                 # HTTP endpoints
│   └── endpoints.py    # FastAPI routes
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

4. **Dependency Injection**
   - FastAPI's dependency injection for database sessions
   - Repository injection into handlers

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

## Contributing Guidelines

When adding a new module:

1. Create module structure following DDD pattern
2. Start with domain layer (models, value objects, services)
3. Implement infrastructure (ORM, repository)
4. Create application layer (CQRS handlers)
5. Add API endpoints
6. Write tests (domain and API)
7. Create migration for database changes
8. Update this documentation

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
