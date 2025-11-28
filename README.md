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

The project maintains 100% test coverage on all implemented modules:

- **Employee Module**: 11 tests (5 domain + 6 API)
- **Contract Module**: 14 tests (8 domain + 6 API)
- **Compensation Module**: 19 tests (10 domain + 9 API)
- **Absence Module**: 29 tests (15 domain + 14 API)

**Total: 73 tests, 100% passing**

## Coding Standards

- No comments in code (code should be self-explanatory)
- Type hints for all function signatures
- Follow DDD principles strictly
- Domain layer has no infrastructure dependencies
- CQRS pattern for application layer
- Repository pattern for data access

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