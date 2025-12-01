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
FR-33: Every resource like Employees,Payroll and etc should have timeline and thre you will se all logs from audit who and what do