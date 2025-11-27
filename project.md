1. 🧩 Business Requirements (BRD)
BR-1: Employee Management

The system must store employees and their employment statuses.
Statuses must have date ranges:

valid_from

valid_to (optional)

Employment status changes affect payroll calculations.

BR-2: Contract Management

The system must support multiple contract types:

fixed monthly salary

hourly

B2B (daily/hourly)

task-based contracts

commission-based contracts

Contracts must have validity intervals and historical versions.
Contracts must never be overwritten.

BR-3: Contract Cancellation & Expiration Notifications

When a contract:

is canceled early, or

reaches its valid_to automatically

The system must notify external systems via RabbitMQ events:

ContractCanceled

ContractExpired

These events must include:

contract ID

employee ID

contract type

expiration/cancellation timestamp

reason (if canceled)

BR-4: Compensation & Rates

The system must support:

base rate history

overtime rules

bonuses

commissions

sick leave reductions (80% rules, etc.)

Every rule must have a validity interval.

BR-5: Absences

System must track:

sick leave

paid time off

unpaid leave

special absence types

Absences must affect compensation.

BR-6: Timesheets

System must ingest timesheets from external systems and support:

daily entries

validation

overtime calculation

BR-7: Payroll Engine

The payroll engine must:

use contract versions and rate versions

consider employee status changes

handle multiple contract types

calculate gross & net

support cycles: monthly, weekly, bi-weekly

handle backdated data changes

maintain payroll history

BR-8: Reporting

The system must generate:

payroll summaries

employee cost reports

month-to-month comparisons

export CSV/PDF files

BR-9: Auditability

All changes must be auditable:

who changed

when

what field changed

BR-10: Event-Driven Integration

System must consume external HR events:

EmployeeAdded

EmployeeUpdated

EmployeeStatusUpdated

ContractCreated

ContractUpdated

TimesheetAdded

AbsenceAdded

And produce:

ContractExpired

ContractCanceled

BR-11: Security & Roles

Provide role-based access:

Admin

HR

Payroll specialist

Authentication: JWT.

2. ⚙️ Functional Requirements (FRD)
Employees

FR-1: Add employee

FR-2: Update employee

FR-3: List employees

FR-4: View employee details

FR-5: Track employment status timeline

Contracts

FR-6: Create contract

FR-7: Update contract (new version)

FR-8: Auto-expire contracts using scheduler

FR-9: HR can cancel contracts

FR-10: Notify external systems on expiration

FR-11: Notify external systems on cancellation

Rates

FR-12: Add base rate

FR-13: Change base rate (new version)

FR-14: Add bonuses, commissions

FR-15: Add rules tied to date ranges

Absences

FR-16: Add absence

FR-17: Validate absence vs employee status

FR-18: Apply absence rules to payroll

Timesheets

FR-19: Add timesheet entry

FR-20: Mark overtime

FR-21: Sum hours in interval

Payroll

FR-22: Run payroll for period

FR-23: Recompute payroll on updated data

FR-24: Store payroll history

FR-25: Provide payroll reports

Integrations

FR-26: Consume HR events

FR-27: Produce integration events

FR-28: Integration retry logic

UI

FR-29: Employees CRUD

FR-30: Contracts CRUD + cancel UI

FR-31: Payroll UI

FR-32: Reports UI

3. 📈 Non-Functional Requirements

NFR-1: Availability 99%

NFR-2: Performance: payroll for 1k employees < 5 seconds

NFR-3: Security: JWT + RBAC

NFR-4: Audit logs immutable

NFR-5: Test coverage: ≥ 80% integration tests

NFR-6: Scalability: queue-driven horizontal scaling

NFR-7: Docker-only local environment

4. 🧱 Technical Requirements (Updated)
Backend

Python

FastAPI

Pydantic v2

SQLAlchemy 2.0

Alembic

PostgreSQL

RabbitMQ

Celery or Dramatiq

Redis (optional but recommended)

Frontend

React

TypeScript

Tailwind CSS

Redux Toolkit (mandatory)

RTK Query recommended for API communication

Architecture Constraints
Use full DDD

Bounded contexts:

Employee

Contract

Compensation

Absence

Timesheet

Payroll

Reporting

Use small services (single responsibility)

Examples:

CreateEmployeeService

ChangeEmployeeStatusService

CreateContractService

CancelContractService

ExpireContractService

ComputePayrollService

Event model

RabbitMQ events:

Incoming:

EmployeeAdded

EmployeeUpdated

ContractCreated

ContractUpdated

TimesheetAdded

AbsenceAdded

Outgoing:

ContractExpired

ContractCanceled

Local Development

Everything must run via Docker Compose only:

backend

worker

frontend

postgres

rabbitmq

redis

migrations container

5. 🧩 DDD Domain Model
Entities
Employee

id

personal info

list of statuses

EmploymentStatus (Value Object)

type

valid_from

valid_to

Contract

id

employee_id

contract_type

rate

validity interval

cancellation status

expiration status

ContractStatus (Value Object)

ACTIVE

EXPIRED

CANCELED

Rate

rate

valid_from

valid_to

Absence

type

valid_from

valid_to

TimesheetEntry

date

hours

PayrollRun

period

results[]

Domain Events

ContractCreated

ContractUpdated

ContractCanceled

ContractExpired

Domain Services

CreateContractService

CancelContractService

ExpireContractService

ContractExpirationCheckerService

ComputePayrollService

6. 🏛 Architecture Overview
ASCII Diagram
External HR System
        │ incoming events
        ▼
   RabbitMQ (exchange: employee.events)
        │
        ▼
  Ingestion Worker
        │
        ▼
 Employee Service
        │
        ├── Contract Service ──┐
        │                     │
        │   outgoing events   ▼
        └──────────────▶ RabbitMQ (contract.events)
                         (ContractExpired,
                          ContractCanceled)


Backend: FastAPI
Workers: Celery/Dramatiq
Storage: PostgreSQL
Cache: Redis
Frontend: React + TS + Tailwind + Redux Toolkit

7. 🧪 Testing Plan
Backend Testing

pytest

pytest-asyncio

httpx

testcontainers (PostgreSQL, RabbitMQ)

Required integration tests:

API endpoints

DB queries

event consumers

event producers

payroll calculations

contract cancellation

contract expiration

expiration scheduler

Frontend Testing

Jest or Vitest

React Testing Library

Optional: Playwright for E2E

Required integration tests:

Redux slices

API queries

Contract cancellation UI flows

8. 🚀 DevOps Plan
CI

lint (ruff + mypy)

test (backend + frontend)

coverage

build docker images

CD (future)

run migrations

deploy backend cluster

deploy frontend

configure environment variables

message queue setup

9. 🗓 Milestones & Timeline
M1: Foundation (1 week)

repo

Docker Compose

backend skeleton (DDD folders)

frontend skeleton

CI pipeline

M2: Employee context (1 week)
M3: Contract context (1–2 weeks)

including cancellation & expiration

outgoing events

M4: Rates & Compensation (1 week)
M5: Absence & Timesheet (1 week)
M6: Payroll Engine (2–3 weeks)
M7: UI Implementation (2 weeks)
M8: Integration & Testing (1–2 weeks)