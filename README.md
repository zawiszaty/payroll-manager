# Payroll Manager

[![codecov](https://codecov.io/gh/zawiszaty/payroll-manager/graph/badge.svg?token=AI8Z9KRF3R)](https://codecov.io/gh/zawiszaty/payroll-manager)

A comprehensive payroll management system built with Domain-Driven Design (DDD) architecture, featuring modular bounded contexts for employee management, contracts, compensation, and more.

## Overview

Payroll Manager is a modern, scalable solution for managing employee data, contracts, compensation structures, and payroll processing. Built with Python 3.14, FastAPI, and PostgreSQL, it follows clean architecture principles and CQRS patterns for maintainability and extensibility.

## Features

### Implemented Modules

- **Employee Management** - Complete employee lifecycle with status tracking
- **Contract Management** - Multiple contract types with lifecycle operations
- **Compensation Management** - Rates, bonuses, deductions, overtime, and sick leave
- **Absence Management** - Leave requests, absence tracking, and balance management

### Key Capabilities

-  RESTful API with automatic OpenAPI documentation
-  Async/await throughout for high performance
-  PostgreSQL with full ACID compliance
-  Message queue integration (RabbitMQ) for event-driven architecture
-  Redis caching support
-  Comprehensive test coverage (100% on all modules)
-  Database migrations with Alembic
-  Docker-based development environment

## Technology Stack

### Backend
- **Python 3.14** - Latest Python with async support
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - Async ORM with type hints
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Pydantic V2** - Data validation and settings

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

The project follows **Domain-Driven Design (DDD)** with clear separation of concerns:

```
app/modules/{module}/
     domain/              # Business logic (pure Python)
         models.py       # Entities and aggregates
         value_objects.py
         repository.py   # Abstract interfaces
         services.py     # Domain services
    infrastructure/      # Technical implementations
        models.py       # ORM models
        repository.py   # Repository implementations
    application/         # Use cases (CQRS)
        commands.py
        queries.py
        handlers.py
    api/                 # HTTP layer
        endpoints.py
    tests/               # Module-specific tests
        test_domain.py
        test_api.py
```

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

# Database
task db-shell        # Open PostgreSQL shell
task migrate         # Run migrations
task reset-db        # Reset database (drops all data)

# Testing
task test                  # Run all tests
task test-employee         # Run employee module tests
task test-contract         # Run contract module tests
task test-compensation     # Run compensation module tests
task test-absence          # Run absence module tests
task test-coverage         # Run tests with coverage report

# Code Quality
task lint            # Run linting
task lint-fix        # Auto-fix linting issues
task format          # Format code
task type-check      # Run type checking

# Utilities
task shell           # Open shell in backend container
task health          # Check service health
task ps              # Show running containers
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
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Redis**: localhost:6379

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

## Contributing

1. Follow the existing DDD architecture
2. Write tests for all new features
3. Ensure all tests pass: `task test`
4. Run linting: `task lint`
5. Format code: `task format`
6. Update documentation as needed

## License

MIT