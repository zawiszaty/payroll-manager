# Reporting Module

Complete DDD-based reporting module for generating and managing reports in various formats.

## Features

- ✅ Multiple report types (Payroll, Compensation, Absence, Timesheet, Tax, Custom)
- ✅ Multiple export formats (PDF, CSV, XLSX, JSON)
- ✅ Report lifecycle management (Pending → Processing → Completed/Failed)
- ✅ File generation with ReportLab (PDF) and openpyxl (Excel)
- ✅ RESTful API with full CRUD operations
- ✅ Inter-module communication via Facade pattern
- ⚠️ **Synchronous generation** (for now - see Future Enhancements for async queue)

## Current Implementation

### Quick Start (Synchronous)

**1. Create a Report**
```bash
curl -X POST http://localhost:8000/api/v1/reporting/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monthly Payroll Report",
    "report_type": "payroll_summary",
    "format": "pdf",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }'
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Monthly Payroll Report",
  "status": "pending",  ← Report created, not yet generated
  ...
}
```

**2. Generate the Report** (This currently blocks until complete)
```bash
curl -X POST http://localhost:8000/api/v1/reporting/123e4567-e89b-12d3-a456-426614174000/generate
```

Response after generation:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",  ← Now completed
  "file_path": "/tmp/reports/report_123e4567_20240130_143022.pdf",
  ...
}
```

**3. Download the File**
```bash
curl -X GET http://localhost:8000/api/v1/reporting/123e4567-e89b-12d3-a456-426614174000/download \
  -o report.pdf
```

---

## ⚠️ Current Limitation

The `/generate` endpoint is **synchronous** - it blocks until the report is complete. For small reports this is fine, but for large reports this is problematic.

## 🚀 Recommended Production Architecture

For production, you should implement:

### 1. Background Job Queue (Celery + RabbitMQ)

```python
# celery_tasks.py
@celery.task
def generate_report_async(report_id: UUID):
    # Fetch report
    # Generate file
    # Update status to COMPLETED/FAILED
    pass
```

### 2. Auto-Trigger on Create

```python
@router.post("/", response_model=ReportResponse)
async def create_report(...):
    report = await handler.handle(command)

    # Automatically queue for generation
    generate_report_async.delay(report.id)

    return ReportResponse.from_entity(report)  # Returns immediately with status=pending
```

### 3. Client Polls for Status

```bash
# Client creates report
POST /api/v1/reporting/ → { "id": "...", "status": "pending" }

# Report queued automatically, client polls
GET /api/v1/reporting/123/  → { "status": "processing" }
GET /api/v1/reporting/123/  → { "status": "processing" }
GET /api/v1/reporting/123/  → { "status": "completed", "file_path": "..." }

# Client downloads
GET /api/v1/reporting/123/download
```

This way:
- ✅ Client doesn't wait for generation
- ✅ Backend handles heavy workload in background
- ✅ Multiple reports can generate in parallel
- ✅ Client can show progress UI ("Generating... 🔄")

## API Endpoints

### Report Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reporting/` | Create a new report |
| GET | `/api/v1/reporting/{id}` | Get report details |
| GET | `/api/v1/reporting/` | List all reports |
| GET | `/api/v1/reporting/type/{type}` | List reports by type |
| GET | `/api/v1/reporting/status/{status}` | List reports by status |
| DELETE | `/api/v1/reporting/{id}` | Delete a report |

### Report Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reporting/{id}/generate` | Generate report file |
| GET | `/api/v1/reporting/{id}/download` | Download generated file |

### Status Management (Manual)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reporting/{id}/start` | Mark as processing |
| POST | `/api/v1/reporting/{id}/complete` | Mark as completed |
| POST | `/api/v1/reporting/{id}/fail` | Mark as failed |

## Report Types

- `payroll_summary` - Employee payroll data with gross pay, deductions, net pay
- `employee_compensation` - Employee compensation breakdown with salary and bonuses
- `absence_summary` - Employee absence records with types and dates
- `timesheet_summary` - Employee timesheet data with regular and overtime hours
- `tax_report` - Tax withholding information
- `custom` - Custom report with flexible data structure

## Export Formats

- **PDF** - Formatted PDF with tables and styling (uses ReportLab)
- **CSV** - Comma-separated values with metadata headers
- **XLSX** - Excel spreadsheet with formatting (uses openpyxl)
- **JSON** - Structured JSON with metadata and data sections

## Report Parameters

Optional filters for data:
- `employee_id` - Filter by specific employee
- `department` - Filter by department
- `start_date` - Start date for date range
- `end_date` - End date for date range
- `additional_filters` - Custom key-value filters

## Architecture

### Domain Layer
- **Report** - Aggregate root managing report lifecycle
- **ReportType**, **ReportFormat**, **ReportStatus** - Value objects
- **IReportGenerator** - Abstract generator interface

### Infrastructure Layer
- **ReportORM** - SQLAlchemy model
- **SQLAlchemyReportRepository** - Repository implementation
- **Report Generators** - PDF, CSV, XLSX, JSON generators
- **ReportGeneratorFactory** - Factory for selecting appropriate generator

### Application Layer
- **Commands & Queries** - CQRS pattern
- **Handlers** - Business logic orchestration
- **ReportGeneratorService** - Report generation coordination

### API Layer
- **IReportingFacade** - Public interface for other modules
- **ReportingFacade** - Implementation with DTOs

### Presentation Layer
- **Routes** - FastAPI endpoints
- **Schemas** - Pydantic request/response models

## File Storage

Generated reports are stored in `/tmp/reports/` with naming format:
```
report_{report_id}_{timestamp}.{format}
```

Example: `report_123e4567-e89b-12d3-a456-426614174000_20240130_143022.pdf`

## Testing

Run tests:
```bash
task test-reporting
```

Test coverage: 22/22 tests passing (100%)
- 11 domain tests
- 11 API integration tests

## Dependencies

- `reportlab` - PDF generation
- `openpyxl` - Excel file generation
- `fastapi` - REST API framework
- `sqlalchemy` - ORM and database

## Future Enhancements

- [ ] Async background job processing with Celery
- [ ] Email delivery of generated reports
- [ ] Report scheduling and recurring reports
- [ ] Custom report templates
- [ ] Data aggregation from multiple modules
- [ ] Report caching and versioning
- [ ] Pagination for large datasets
- [ ] Chart and graph generation
