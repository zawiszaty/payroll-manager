# Payroll Manager

[![codecov](https://codecov.io/gh/zawiszaty/payroll-manager/graph/badge.svg?token=AI8Z9KRF3R)](https://codecov.io/gh/zawiszaty/payroll-manager)

A comprehensive payroll management system built with Domain-Driven Design (DDD) and Event-Driven Architecture, featuring modular bounded contexts for employee management, contracts, compensation, timesheets, and payroll processing. Designed for scalability, auditability, and integration with external HR systems.

## Overview

Payroll Manager is a modern, scalable solution for managing employee data, contracts, compensation structures, and payroll processing. Built with Python 3.14, FastAPI, and PostgreSQL, it follows clean architecture principles and CQRS patterns for maintainability and extensibility.

## Project Structure

```
payroll-manager/
├── backend/                    # Python backend application
│   ├── app/
│   │   ├── modules/           # Bounded contexts (DDD modules)
│   │   │   ├── employee/      # Employee management
│   │   │   ├── contract/      # Contract lifecycle
│   │   │   ├── compensation/  # Rates, bonuses, deductions
│   │   │   ├── absence/       # Leave management
│   │   │   ├── timesheet/     # Time tracking
│   │   │   ├── payroll/       # Payroll processing
│   │   │   ├── reporting/     # Report generation
│   │   │   ├── audit/         # Audit logging
│   │   │   └── auth/          # Authentication & authorization
│   │   ├── shared/            # Shared infrastructure
│   │   │   ├── domain/        # Base domain classes
│   │   │   └── infrastructure/# Event bus, consumers, RabbitMQ
│   │   ├── api/               # API versioning and routing
│   │   ├── database.py        # Database configuration
│   │   ├── config.py          # Application settings
│   │   └── main.py            # FastAPI application entry point
│   ├── migrations/            # Alembic database migrations
│   ├── scripts/               # Utility scripts
│   ├── tests/                 # Integration tests
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React TypeScript frontend
│   ├── src/
│   │   ├── features/          # Feature modules (by domain)
│   │   │   ├── employees/
│   │   │   ├── contracts/
│   │   │   ├── compensation/
│   │   │   ├── absences/
│   │   │   ├── timesheets/
│   │   │   ├── payroll/
│   │   │   ├── reporting/
│   │   │   └── auth/
│   │   ├── components/        # Shared UI components
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   ├── layout/       # Layout components
│   │   │   └── common/       # Reusable components
│   │   ├── api/              # API client and endpoints
│   │   ├── routes/           # React Router configuration
│   │   └── test/             # Test utilities
│   └── package.json
├── scripts/                   # Project-level scripts
├── docker-compose.yml         # Docker services configuration
├── Taskfile.yml              # Task automation (task runner)
└── README.md                 # This file
```

## Features

### Implemented Modules

- **Employee Management** - Complete employee lifecycle with status tracking and employment history
- **Contract Management** - Multiple contract types (fixed salary, hourly, B2B, task-based, commission) with versioning and lifecycle operations
- **Compensation Management** - Rates, bonuses, deductions, overtime, and sick leave with historical tracking
- **Absence Management** - Leave requests, absence tracking, balance management, and approval workflows
- **Timesheet Management** - Time tracking, overtime calculation, approval workflows, and hours summaries
- **Payroll Processing** - Automated payroll calculation supporting multiple contract types, monthly/weekly/bi-weekly cycles
- **Reporting** - Payroll summaries, employee cost reports, month-to-month comparisons with CSV/PDF exports
- **Audit Logging** - Complete audit trail for all entity changes with who/what/when tracking
- **Authentication & Authorization** - JWT-based auth with role-based access control (Admin, HR, Payroll Specialist)

### Key Capabilities

- **RESTful API** with automatic OpenAPI documentation (Swagger/ReDoc)
- **Async/await** throughout for high performance
- **PostgreSQL** with full ACID compliance and optimized indexes
- **Event-Driven Architecture** using RabbitMQ for module communication
- **Redis caching** for improved query performance
- **Comprehensive test coverage** - 100% coverage on all modules
- **Database migrations** with Alembic for version control
- **Docker-based development** environment with hot-reload
- **JWT Authentication** with refresh tokens and role-based access control
- **Audit logging** for all entity changes (who, what, when)
- **Type safety** - Full type hints (Python) and TypeScript (frontend)
- **Scheduler** for automated tasks (contract expiration, payroll runs)

## Technology Stack

### Backend
- **Python 3.14** - Latest Python with async support
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - Async ORM with type hints
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Pydantic V2** - Data validation and settings

### Frontend
- **React 18** - UI framework with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Re-usable component library
- **Vitest** - Unit testing framework
- **Testing Library** - React component testing

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **RabbitMQ** - Message broker for async processing
- **Redis** - Caching layer
- **Taskfile** - Task automation

### Development
- **pytest** - Testing framework with async support
- **ruff** - Fast Python linter and formatter
- **mypy** - Static type checking

## Architecture

The project follows **Domain-Driven Design (DDD)** with **Event-Driven Architecture** and clear separation of concerns using **Bounded Contexts**.

### Architectural Patterns

- **Domain-Driven Design (DDD)** - Business logic isolated in domain layer
- **CQRS (Command Query Responsibility Segregation)** - Separate read and write models
- **Event-Driven Architecture** - Asynchronous communication between modules via domain events
- **Repository Pattern** - Data access abstraction
- **Facade Pattern** - Clean module boundaries and inter-module communication
- **Hexagonal Architecture** - Domain independent from infrastructure

### Module Structure (Bounded Contexts)

Each module is a separate bounded context with its own domain model:

```
app/modules/{module}/
    domain/                      # Business logic (pure Python)
        models.py               # Entities and aggregates
        value_objects.py        # Value objects (immutable)
        repository.py           # Abstract repository interfaces
        services.py             # Domain services
        events.py               # Domain events
    infrastructure/              # Technical implementations
        models.py               # ORM models (SQLAlchemy)
        repository.py           # Repository implementations
        read_model.py           # Query/read model for CQRS
        event_handlers.py       # Domain event handlers
        adapters.py             # External service adapters
    application/                 # Use cases (CQRS)
        commands.py             # Write operations
        queries.py              # Read operations
        handlers.py             # Command/query handlers
    api/                         # API layer
        facade.py               # Public API for other modules
    presentation/                # HTTP layer
        endpoints.py            # FastAPI routes
        views.py                # Response models
    tests/                       # Module-specific tests
        test_domain.py
        test_api.py
```

### Domain Events and Event-Driven Communication

Modules communicate asynchronously through **Domain Events** published to **RabbitMQ**:

#### Core Domain Events

**Employee Module:**
- `EmployeeCreated` - New employee added
- `EmployeeUpdated` - Employee data changed
- `EmployeeStatusChanged` - Employment status modified

**Contract Module:**
- `ContractCreated` - New contract created
- `ContractUpdated` - Contract terms modified
- `ContractExpired` - Contract reached end date (auto-scheduled)
- `ContractCanceled` - Contract terminated early

**Absence Module:**
- `AbsenceRequested` - New absence request (from external systems)
- `AbsenceApproved` - Absence request approved
- `AbsenceRejected` - Absence request rejected
- `AbsenceBalanceUpdated` - Balance changed

**Compensation Module:**
- `RateCreated` - New compensation rate added
- `RateUpdated` - Rate modified
- `BonusCreated` - Bonus added

**Timesheet Module:**
- `TimesheetCreated` - New timesheet entry
- `TimesheetApproved` - Timesheet approved
- `TimesheetRejected` - Timesheet rejected

**Payroll Module:**
- `PayrollCalculated` - Payroll run completed
- `PayrollApproved` - Payroll approved for payment
- `PayrollPaid` - Payroll marked as paid

**Audit Module:**
- `AuditLogCreated` - Entity change recorded

#### Event Flow Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Domain    │────────>│   RabbitMQ   │────────>│   Event     │
│   Module    │ Publish │   Exchange   │ Consume │  Consumer   │
└─────────────┘         └──────────────┘         └─────────────┘
                                                          │
                                                          ▼
                                                  ┌───────────────┐
                                                  │Event Registry │
                                                  │   Handlers    │
                                                  └───────────────┘
```

The system uses a **Unified Event Consumer** that:
1. Listens to all event queues from RabbitMQ
2. Routes events to registered handlers via the Event Registry
3. Enables loose coupling between modules
4. Supports external system integration (HR systems, time tracking tools)

### Inter-Module Communication

Modules never directly import domain objects from other modules. Instead, they:

1. **Facade Pattern** - Use public facades (e.g., `EmployeeApiFacade`) for synchronous queries
2. **Domain Events** - Publish events for asynchronous operations
3. **Anti-Corruption Layer** - Adapters translate between module contexts

### Scheduled Tasks

The system includes background schedulers for:

- **Contract Expiration** - Auto-expires contracts when `valid_to` date is reached
- **Month-End Processing** - Automated payroll calculations (configurable)
- **Report Generation** - Scheduled report creation

### Data Flow Example: Creating a Payroll

Here's how the system processes a payroll calculation through multiple bounded contexts:

```
1. API Request (Frontend/Client)
   └─> POST /api/v1/payroll/ {employee_id, period}

2. Application Layer (CQRS Command)
   └─> CreatePayrollCommand
       └─> CreatePayrollHandler
           ├─> Fetch employee via EmployeeApiFacade
           ├─> Fetch active contract via ContractApiFacade
           ├─> Fetch rates via CompensationApiFacade
           ├─> Fetch absences via AbsenceApiFacade
           ├─> Fetch timesheets via TimesheetApiFacade
           └─> Domain Service: PayrollCalculationService
               └─> Calculate gross/net, deductions, bonuses

3. Domain Layer
   └─> Payroll aggregate created
       └─> Emits: PayrollCalculated event

4. Infrastructure Layer
   ├─> Save to database (Repository)
   └─> Publish event to RabbitMQ

5. Event Consumer
   └─> Receives PayrollCalculated event
       └─> AuditLogHandler creates audit entry
       └─> ReportingHandler updates statistics
```

### Data Consistency and Transactions

- **Within Module** - ACID transactions via PostgreSQL
- **Cross-Module** - Eventual consistency via domain events
- **Compensating Actions** - Events can trigger rollback workflows
- **Idempotency** - Event handlers designed to be idempotent
- **Retry Logic** - Failed events automatically retried by RabbitMQ

### Key Design Decisions

**Immutable History**
- Contracts are never updated in place - new versions created instead
- Rates maintain historical records with validity periods
- Employment status changes tracked with date ranges
- Enables accurate historical payroll recalculation

**Eventual Consistency**
- Modules loosely coupled through events
- Enables independent scaling and deployment
- Audit logs created asynchronously
- Trade-off: slight delay in cross-module data propagation

**No Cascading Deletes**
- Entities marked as inactive/canceled rather than deleted
- Preserves audit trail and historical accuracy
- Enables compliance and regulatory reporting

**Read Models (CQRS)**
- Separate optimized read models for queries
- Write operations use domain models
- Improves query performance for complex reports
- Simplifies API response formatting

## Getting Started

### Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- [Task](https://taskfile.dev/) (optional, for convenience commands)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd payroll-manager
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` if needed (default values work for local development)

3. **Start all services**
   ```bash
   # Using Task (recommended)
   task up

   # Or using Docker Compose directly
   docker compose up -d
   ```

4. **Verify installation**
   ```bash
   task health
   # Or
   curl http://localhost:8000/health
   ```

5. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

6. **Start the frontend (optional)**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   The frontend will be available at http://localhost:5173

### Login Credentials

For development and testing, use the following credentials:

**Admin Account:**
- Email: `admin@example.com`
- Password: `admin123`

**Test Account:**
- Email: `test@example.com`
- Password: `testpassword123`

You can create additional users using the CLI:
```bash
docker exec -it payroll_backend python -m app.modules.auth.presentation.cli create user@example.com --password yourpassword --role admin --full-name "Your Name"
```

### Initial Setup

The application automatically runs migrations on startup. For manual migration management:

```bash
# Create a new migration
task migrate-create -- "description"

# Run migrations
task migrate

# Rollback one migration
task migrate-downgrade
```

## Development

### Available Commands

```bash
# Service Management
task up              # Start all services
task down            # Stop all services
task restart         # Restart all services
task logs            # View logs from all services
task logs-backend    # View backend logs only
task ps              # Show running containers
task health          # Check service health

# Database
task db-shell        # Open PostgreSQL shell
task migrate         # Run migrations
task migrate-create  # Create new migration
task reset-db        # Reset database (drops all data)

# Backend Testing
task test                  # Run all backend tests
task test-employee         # Run employee module tests
task test-contract         # Run contract module tests
task test-compensation     # Run compensation module tests
task test-absence          # Run absence module tests
task test-timesheet        # Run timesheet module tests
task test-reporting        # Run reporting module tests
task test-coverage         # Run tests with coverage report

# Backend Code Quality
task lint            # Run linting
task lint-fix        # Auto-fix linting issues
task format          # Format code
task format-check    # Check code formatting
task type-check      # Run type checking

# Frontend Development
task frontend-install      # Install frontend dependencies
task frontend-dev          # Start frontend dev server (http://localhost:5173)
task frontend-build        # Build frontend for production

# Frontend Testing
task frontend-test                # Run frontend tests
task frontend-test-watch          # Run frontend tests in watch mode
task frontend-test-ui             # Run frontend tests with UI
task frontend-test-coverage       # Run frontend tests with coverage

# Frontend Code Quality
task frontend-lint             # Run frontend linting
task frontend-lint-fix         # Auto-fix frontend linting issues
task frontend-format           # Format frontend code
task frontend-format-check     # Check frontend code formatting
task frontend-typecheck        # Run frontend type checking

# Combined Tasks
task test-all        # Run all tests (backend + frontend)
task lint-all        # Run all linting (backend + frontend)
task format-all      # Format all code (backend + frontend)
task check-all       # Run all checks (lint, format, type-check, tests)
task ci              # Run full CI pipeline locally (backend + frontend)
task ci-backend      # Run backend CI pipeline only
task ci-frontend     # Run frontend CI pipeline only

# Utilities
task shell           # Open shell in backend container
task api-docs        # Open API documentation in browser
```

### Running Tests

```bash
# All tests
task test

# Specific module
task test-employee
task test-contract
task test-compensation
task test-absence

# With coverage
task test-coverage

# Inside container (more options)
docker compose exec backend pytest app/modules/employee/tests/ -v
```

### Development Workflow

1. **Make changes** to the code
2. **Run tests** to verify: `task test`
3. **Check code quality**: `task lint && task type-check`
4. **Format code**: `task format`
5. **Create migration** if needed: `task migrate-create -- "description"`
6. **Commit changes** following conventional commits

## Event-Driven Architecture

The system uses RabbitMQ for event-driven communication, allowing external systems to integrate seamlessly.

### Simulating External Absence Requests

You can simulate an external HR system creating absence requests using the provided script:

```bash
# Basic usage with defaults (vacation, tomorrow, 3 days)
./scripts/publish_absence_event.sh <employee-id>

# With custom parameters
./scripts/publish_absence_event.sh 6943b9a0-5c0e-4379-9c09-e73c6ba6d881 \
  --absence-type sick_leave \
  --start-date 2025-12-15 \
  --end-date 2025-12-20 \
  --reason "Medical appointment"

# Available absence types:
# vacation, sick_leave, parental_leave, unpaid_leave, bereavement, study_leave, compassionate

# You can also call the Python script directly:
docker exec payroll_backend python /app/scripts/publish_absence_request_event.py <employee-id> [options]
```

The script will:
1. Publish an `AbsenceRequestedEvent` to RabbitMQ
2. The event consumer will automatically create a pending absence request
3. The request will appear in the frontend at http://localhost:5173/absences
4. Managers can then approve or reject the request

This demonstrates how external systems (like HR platforms, time-tracking tools, or employee self-service portals) can integrate with the payroll system through events.

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://payroll_user:payroll_pass@postgres:5432/payroll_db

# Message Queue
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# Cache
REDIS_URL=redis://redis:6379/0

# Security (change in production!)
SECRET_KEY=your-secret-key-change-in-production

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Service Ports

- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Frontend**: http://localhost:5173 (development mode)
- **PostgreSQL**: localhost:5432
- **RabbitMQ Management**: http://localhost:15672 (username: `payroll`, password: `payroll`)
- **Redis**: localhost:6379

### Running Services

The Docker Compose setup includes the following services:

1. **postgres** - PostgreSQL database
2. **rabbitmq** - RabbitMQ message broker with management UI
3. **redis** - Redis cache
4. **backend** - FastAPI application server
5. **event_consumer** - Dedicated event consumer service for processing domain events

The event consumer runs as a separate container to ensure event processing continues independently of the main API service.

## Security

### Authentication & Authorization

**Authentication:**
- **JWT (JSON Web Tokens)** - Stateless authentication
- **Access Tokens** - Short-lived (configurable expiration)
- **Refresh Tokens** - Long-lived tokens for obtaining new access tokens
- **Password Hashing** - bcrypt for secure password storage
- **Token Blacklisting** - Support for token revocation

**Authorization (RBAC):**
- **Admin** - Full system access, user management, configuration
- **HR** - Employee management, contract operations, absence approval
- **Payroll Specialist** - Payroll processing, compensation management, reporting
- **Read-Only Roles** - View-only access for auditors

**API Security:**
- **CORS** - Configurable allowed origins
- **Rate Limiting** - Prevent abuse (configurable)
- **Input Validation** - Pydantic models for request validation
- **SQL Injection Prevention** - ORM-based queries (SQLAlchemy)
- **XSS Protection** - Response sanitization

**Development vs Production:**
- Default credentials provided for development only
- Environment-based configuration
- Secret key rotation supported
- Database credentials isolated per environment

### Creating Users

Create users via CLI:

```bash
# Create admin user
docker exec -it payroll_backend python -m app.modules.auth.presentation.cli create admin@company.com --password securepass123 --role admin --full-name "Admin User"

# Create HR user
docker exec -it payroll_backend python -m app.modules.auth.presentation.cli create hr@company.com --password hrpass123 --role hr --full-name "HR Manager"

# Create payroll specialist
docker exec -it payroll_backend python -m app.modules.auth.presentation.cli create payroll@company.com --password payrollpass123 --role payroll_specialist --full-name "Payroll User"
```

## Testing

The project maintains comprehensive test coverage across all modules with **212 tests, 100% passing**.

### Test Database Configuration

Tests use environment variables for database configuration. The following variables can be set to customize the test database connection:

```env
# Test Database Configuration (optional - defaults provided)
TEST_DB_USER=payroll_user          # Database user (default: payroll_user)
TEST_DB_PASSWORD=payroll_pass      # Database password (default: payroll_pass)
TEST_DB_HOST=postgres              # Database host (default: postgres)
TEST_DB_PORT=5432                  # Database port (default: 5432)
TEST_DB_NAME=payroll_db_test       # Test database name (default: payroll_db_test)
```

**Note**: The default values work for the Docker Compose environment. Override these variables in CI/CD pipelines or different environments as needed.

If required variables are missing and no defaults can be used, tests will fail fast with a clear error message indicating which environment variables need to be set.

## Frontend Development

### Frontend Architecture

The frontend is built with React, TypeScript, and Vite, following a feature-based modular architecture:

```
frontend/src/
├── api/                    # API client and endpoints
│   ├── client.ts          # Axios client with interceptors
│   ├── auth.ts            # Authentication API
│   ├── employees.ts       # Employee API wrapper
│   ├── contracts.ts       # Contract API wrapper
│   └── audit.ts           # Audit API wrapper
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── common/            # Shared components (AuditHistory, etc.)
│   └── layout/            # Layout components (Header, Sidebar)
├── features/              # Feature modules
│   ├── auth/
│   ├── employees/
│   ├── contracts/
│   └── dashboard/
├── lib/                   # Utilities and helpers
├── routes/               # React Router configuration
└── test/                 # Test utilities and setup
```

### Creating New Frontend Modules

When adding a new feature module (e.g., timesheets, payroll), follow these steps:

#### 1. Module Structure

Create the following directory structure:

```bash
frontend/src/features/{module-name}/
├── components/
│   ├── {Module}List.tsx       # List view component
│   ├── {Module}Detail.tsx     # Detail view component
│   ├── {Module}Form.tsx       # Create/edit form
│   └── __tests__/             # Component tests
│       ├── {Module}List.test.tsx
│       ├── {Module}Detail.test.tsx
│       └── {Module}Form.test.tsx
├── hooks/                     # Custom hooks (optional)
│   └── use{Module}s.ts
└── types.ts                   # TypeScript types (if needed)
```

#### 2. API Integration

Create an API wrapper in `frontend/src/api/{module}.ts`:

```typescript
import apiClient from './client'
import type {
  {Module}ListResponse,
  {Module}DetailView,
  Create{Module}Request
} from '@/lib/api'

export const {module}Api = {
  list: async (page = 1, limit = 100): Promise<{Module}ListResponse> => {
    const response = await apiClient.get<{Module}ListResponse>('/{modules}/', {
      params: { page, limit },
    })
    return response.data
  },

  getById: async (id: string): Promise<{Module}DetailView> => {
    const response = await apiClient.get<{Module}DetailView>(`/{modules}/${id}`)
    return response.data
  },

  create: async (data: Create{Module}Request): Promise<{Module}DetailView> => {
    const response = await apiClient.post<{Module}DetailView>('/{modules}/', data)
    return response.data
  },

  // Add other methods as needed
}
```

#### 3. Component Implementation

**List Component** - Display items in a table/grid:
```typescript
// Example: {Module}List.tsx
import { useState, useEffect } from 'react'
import { {module}Api } from '@/api/{module}'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useNavigate } from 'react-router-dom'

export function {Module}List() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadItems()
  }, [])

  const loadItems = async () => {
    try {
      setLoading(true)
      const response = await {module}Api.list()
      setItems(response.items || [])
    } catch (error) {
      console.error('Failed to load {modules}:', error)
    } finally {
      setLoading(false)
    }
  }

  // Render implementation...
}
```

**Detail Component** - Display single item with audit history:
```typescript
// Example: {Module}Detail.tsx
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { {module}Api } from '@/api/{module}'
import { auditApi } from '@/api/audit'
import { AuditHistory } from '@/components/common/AuditHistory'
import { Button } from '@/components/ui/button'
import { History } from 'lucide-react'

export function {Module}Detail() {
  const { id } = useParams<{ id: string }>()
  const [item, setItem] = useState(null)
  const [showHistory, setShowHistory] = useState(false)
  const [auditLogs, setAuditLogs] = useState([])

  useEffect(() => {
    if (id && showHistory) {
      loadAuditHistory()
    }
  }, [id, showHistory])

  const loadAuditHistory = async () => {
    if (!id) return
    try {
      const logs = await auditApi.getByEntity('{module}', id)
      setAuditLogs(logs)
    } catch (error) {
      console.error('Failed to load audit history:', error)
    }
  }

  // Render with "Show History" button and AuditHistory component
}
```

#### 4. Testing Requirements

**ALL new modules MUST include comprehensive tests covering:**

##### Component Tests (`*.test.tsx`)

```typescript
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import { {Module}List } from '../{Module}List'
import { {module}Api } from '@/api/{module}'

vi.mock('@/api/{module}')

describe('{Module}List', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state', () => {
    render(
      <MemoryRouter>
        <{Module}List />
      </MemoryRouter>
    )
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('should load and display items', async () => {
    const mockItems = [{ id: '1', name: 'Test Item' }]
    vi.mocked({module}Api.list).mockResolvedValue({
      items: mockItems,
      total: 1,
      page: 1,
      limit: 100
    })

    render(
      <MemoryRouter>
        <{Module}List />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getByText('Test Item')).toBeInTheDocument()
    })
  })

  it('should handle errors gracefully', async () => {
    vi.mocked({module}Api.list).mockRejectedValue(new Error('API Error'))

    render(
      <MemoryRouter>
        <{Module}List />
      </MemoryRouter>
    )

    await waitFor(() => {
      // Verify error handling
    })
  })

  // Add more tests for user interactions, filtering, sorting, etc.
})
```

##### API Tests (`api/__tests__/{module}.test.ts`)

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { {module}Api } from '../{module}'
import apiClient from '../client'

vi.mock('../client')

describe('{module}Api', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('list', () => {
    it('should fetch {modules} with default pagination', async () => {
      const mockResponse = {
        items: [],
        total: 0,
        page: 1,
        limit: 100
      }
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse })

      const result = await {module}Api.list()

      expect(apiClient.get).toHaveBeenCalledWith('/{modules}/', {
        params: { page: 1, limit: 100 },
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle API errors', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'))

      await expect({module}Api.list()).rejects.toThrow('Network error')
    })
  })

  // Add tests for all API methods
})
```

##### Audit Integration Tests

```typescript
describe('{Module}Detail - Audit Integration', () => {
  it('should not load audit logs on initial render', async () => {
    render{Module}Detail()

    await waitFor(() => {
      expect(screen.getByText('{Module} Details')).toBeInTheDocument()
    })

    expect(auditApi.getByEntity).not.toHaveBeenCalled()
  })

  it('should load audit logs when show history is clicked', async () => {
    vi.mocked(auditApi.getByEntity).mockResolvedValue([])
    render{Module}Detail()

    await waitFor(() => {
      expect(screen.getByText('Show History')).toBeInTheDocument()
    })

    const showHistoryButton = screen.getByText('Show History')
    fireEvent.click(showHistoryButton)

    await waitFor(() => {
      expect(auditApi.getByEntity).toHaveBeenCalledWith('{module}', expect.any(String))
    })
  })

  it('should display audit history after loading', async () => {
    const mockLogs = [{ id: '1', action: 'created', /* ... */ }]
    vi.mocked(auditApi.getByEntity).mockResolvedValue(mockLogs)

    render{Module}Detail()
    fireEvent.click(screen.getByText('Show History'))

    await waitFor(() => {
      expect(screen.getByText('Change History')).toBeInTheDocument()
    })
  })
})
```

#### 5. Test Coverage Requirements

- **Minimum Coverage**: 80% for all new modules
- **Component Tests**: Test rendering, user interactions, loading states, error handling
- **API Tests**: Test all API methods, error handling, response parsing
- **Integration Tests**: Test component + API integration, audit integration
- **Edge Cases**: Test empty states, null values, error scenarios

Run tests:
```bash
# Run all tests
npm test

# Run specific module tests
npm test -- {Module}

# Run with coverage
npm run test:coverage

# Watch mode (for development)
npm test -- --watch
```

#### 6. Routes Configuration

Add routes in `frontend/src/routes/index.tsx`:

```typescript
import { {Module}List } from '@/features/{modules}/components/{Module}List'
import { {Module}Detail } from '@/features/{modules}/components/{Module}Detail'
import { {Module}Form } from '@/features/{modules}/components/{Module}Form'

// In routes array:
{
  path: '/{modules}',
  element: <{Module}List />,
},
{
  path: '/{modules}/new',
  element: <{Module}Form />,
},
{
  path: '/{modules}/:id',
  element: <{Module}Detail />,
},
```

#### 7. Navigation Integration

Add navigation link in `frontend/src/components/layout/Sidebar.tsx`:

```typescript
import { /* icon */ } from 'lucide-react'

// In navigation items:
{
  name: '{Modules}',
  href: '/{modules}',
  icon: /* appropriate icon */,
}
```

#### 8. Audit Integration (Required for all entities)

Every detail view MUST include audit history integration:

1. **Import AuditHistory component**:
   ```typescript
   import { AuditHistory } from '@/components/common/AuditHistory'
   import { auditApi } from '@/api/audit'
   ```

2. **Add state management**:
   ```typescript
   const [showHistory, setShowHistory] = useState(false)
   const [auditLogs, setAuditLogs] = useState([])
   const [auditLoading, setAuditLoading] = useState(false)
   ```

3. **Load audit logs on demand**:
   ```typescript
   useEffect(() => {
     if (id && showHistory) {
       loadAuditHistory()
     }
   }, [id, showHistory])
   ```

4. **Add Show/Hide History button**:
   ```typescript
   <Button variant="outline" onClick={() => setShowHistory(!showHistory)}>
     <History className="mr-2 h-4 w-4" />
     {showHistory ? 'Hide History' : 'Show History'}
   </Button>
   ```

5. **Render audit history**:
   ```typescript
   {showHistory && (
     <AuditHistory auditLogs={auditLogs} isLoading={auditLoading} />
   )}
   ```

### Frontend Development Workflow

1. **Generate TypeScript types** from backend OpenAPI schema:
   ```bash
   cd frontend
   curl http://localhost:8000/openapi.json > openapi.json
   npx openapi-typescript-codegen --input ./openapi.json --output ./src/lib/api --client axios
   ```

2. **Create API wrapper** with type-safe methods

3. **Implement components** following existing patterns

4. **Write comprehensive tests** (required!)

5. **Run tests and verify coverage**:
   ```bash
   npm test
   npm run test:coverage
   ```

6. **Type check**:
   ```bash
   npm run type-check
   ```

7. **Lint and format**:
   ```bash
   npm run lint
   npm run format
   ```

8. **Build and verify**:
   ```bash
   npm run build
   ```

### Frontend Testing Commands

```bash
# Run all tests
npm test

# Run specific test file
npm test -- AuditHistory.test

# Run tests matching pattern
npm test -- audit

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test -- --watch

# Run in UI mode (interactive)
npm test -- --ui
```

### Frontend Code Quality Standards

- **TypeScript**: All code must be TypeScript with proper types
- **No `any` types**: Use proper type definitions from generated API types
- **Component Structure**: Follow functional components with hooks
- **State Management**: Use React hooks (useState, useEffect, etc.)
- **Error Handling**: Always handle loading and error states
- **Accessibility**: Use semantic HTML and ARIA labels where needed
- **Responsive Design**: All components must work on mobile and desktop
- **Testing**: Minimum 80% coverage, all critical paths tested
- **No Console Logs**: Remove or guard console logs in production code

## Coding Standards

### Backend

- No comments in code (code should be self-explanatory)
- Type hints for all function signatures
- Follow DDD principles strictly
- Domain layer has no infrastructure dependencies
- CQRS pattern for application layer
- Repository pattern for data access

### Frontend

- TypeScript with strict mode
- Functional components with hooks
- Type-safe API calls using generated types
- Comprehensive test coverage (minimum 80%)
- Responsive design with Tailwind CSS
- Audit integration for all entity detail views
- Error boundaries for error handling
- Loading states for async operations

## Troubleshooting

### Services won't start
```bash
task down-volumes  # Remove all volumes
task up            # Start fresh
```

### Database connection issues
```bash
task logs          # Check logs
task db-shell      # Test database connection
```

### Tests failing
```bash
task down-volumes  # Clean slate
task up
task test
```

### Permission denied on entrypoint.sh
```bash
chmod +x backend/entrypoint.sh
```

## Production Considerations

### Performance Optimization

**Database:**
- Indexes on frequently queried fields (employee_id, date ranges, status)
- Connection pooling configured (SQLAlchemy async)
- Query optimization for complex reports
- Pagination for all list endpoints

**Caching:**
- Redis for frequently accessed data
- Employee and contract lookups cached
- Cache invalidation on entity updates
- Configurable TTL per cache type

**API Performance:**
- Async/await throughout the stack
- Database queries optimized with eager loading
- Bulk operations for batch processing
- Background tasks for long-running operations

### Monitoring & Observability

**Logging:**
- Structured logging (JSON format in production)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Request/response logging
- Event processing logs

**Health Checks:**
- `/health` endpoint for service health
- Database connectivity check
- RabbitMQ connectivity check
- Redis connectivity check

**Metrics to Monitor:**
- API response times
- Event processing lag
- Database connection pool usage
- RabbitMQ queue depths
- Memory and CPU usage per service

### Deployment

**Environment Variables:**
- All secrets via environment variables
- No hardcoded credentials
- Database URLs per environment
- CORS origins per environment

**Scaling:**
- Backend API - Horizontal scaling (stateless)
- Event Consumer - Multiple instances supported
- Database - Read replicas for reporting
- RabbitMQ - Clustered setup for HA

**Backup & Recovery:**
- Regular PostgreSQL backups
- Transaction logs for point-in-time recovery
- Event replay capability via RabbitMQ
- Audit logs for compliance

### CI/CD Pipeline

The project includes GitHub Actions workflows for:

- **Backend CI** - Linting, type checking, testing, coverage
- **Frontend CI** - Linting, type checking, testing, build
- **Code Coverage** - Codecov integration (badge above)
- **Docker Builds** - Automated container builds

Run CI locally before pushing:

```bash
# Full CI pipeline
task ci

# Backend only
task ci-backend

# Frontend only
task ci-frontend
```

## Contributing

1. **Follow the DDD architecture** - Maintain bounded context isolation
2. **Write comprehensive tests** - Aim for 100% coverage on new code
3. **Use conventional commits** - `feat:`, `fix:`, `docs:`, `refactor:`, etc.
4. **Run CI checks** before pushing: `task check-all`
5. **Update documentation** - Keep README and inline docs current
6. **Add audit logging** - Ensure all entity changes are auditable
7. **Follow coding standards** - Backend (no comments, type hints) / Frontend (TypeScript, 80% coverage)

### Pull Request Checklist

- [ ] Tests added and passing (`task test-all`)
- [ ] Code formatted (`task format-all`)
- [ ] Linting passed (`task lint-all`)
- [ ] Type checking passed (`task type-check` and `task frontend-typecheck`)
- [ ] Documentation updated
- [ ] Migration created if schema changed (`task migrate-create`)
- [ ] Audit logging added for entity changes
- [ ] Frontend tests include audit integration

## License

MIT