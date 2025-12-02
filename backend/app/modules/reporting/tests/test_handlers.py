"""Tests for reporting handlers"""

from datetime import date
from uuid import uuid4

import pytest

from app.modules.reporting.application.commands import (
    CreateReportCommand,
    DeleteReportCommand,
)
from app.modules.reporting.application.handlers import (
    CreateReportHandler,
    DeleteReportHandler,
    ListReportsByStatusHandler,
    ListReportsByTypeHandler,
)
from app.modules.reporting.application.queries import (
    ListReportsByStatusQuery,
    ListReportsByTypeQuery,
)
from app.modules.reporting.domain.entities import Report
from app.modules.reporting.domain.value_objects import (
    ReportFormat,
    ReportParameters,
    ReportStatus,
    ReportType,
)
from app.modules.reporting.infrastructure.repository import SQLAlchemyReportRepository


@pytest.mark.asyncio
async def test_create_report_with_invalid_start_date(test_session):
    """Test that CreateReportHandler validates start_date format"""
    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)

    command = CreateReportCommand(
        name="Test Report",
        report_type="payroll_summary",
        format="pdf",
        start_date="invalid-date",  # Invalid date format
    )

    with pytest.raises(ValueError, match="Invalid start_date format"):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_create_report_with_invalid_end_date(test_session):
    """Test that CreateReportHandler validates end_date format"""
    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)

    command = CreateReportCommand(
        name="Test Report",
        report_type="payroll_summary",
        format="pdf",
        end_date="not-a-date",  # Invalid date format
    )

    with pytest.raises(ValueError, match="Invalid end_date format"):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_create_report_with_valid_dates(test_session):
    """Test CreateReportHandler with valid date strings"""
    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)

    command = CreateReportCommand(
        name="Test Report",
        report_type="payroll_summary",
        format="pdf",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    report = await handler.handle(command)
    await test_session.commit()

    assert report.name == "Test Report"
    assert report.parameters.start_date == date(2024, 1, 1)
    assert report.parameters.end_date == date(2024, 1, 31)


@pytest.mark.asyncio
async def test_delete_report_not_found(test_session):
    """Test DeleteReportHandler raises ValueError when report not found"""
    repository = SQLAlchemyReportRepository(test_session)
    handler = DeleteReportHandler(repository)

    non_existent_id = uuid4()
    command = DeleteReportCommand(report_id=non_existent_id)

    with pytest.raises(ValueError, match=f"Report {non_existent_id} not found"):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_delete_report_success(test_session):
    """Test DeleteReportHandler successfully deletes a report"""
    repository = SQLAlchemyReportRepository(test_session)
    handler = DeleteReportHandler(repository)

    # Create a report first
    params = ReportParameters()
    report = Report(
        name="Report to Delete",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        parameters=params,
    )
    await repository.save(report)
    await test_session.commit()

    # Delete it
    command = DeleteReportCommand(report_id=report.id)
    await handler.handle(command)
    await test_session.commit()

    # Verify it's deleted
    deleted_report = await repository.get_by_id(report.id)
    assert deleted_report is None


@pytest.mark.asyncio
async def test_list_reports_by_type_with_invalid_type(test_session):
    """Test ListReportsByTypeHandler with invalid report type"""
    repository = SQLAlchemyReportRepository(test_session)
    handler = ListReportsByTypeHandler(repository)

    query = ListReportsByTypeQuery(report_type="invalid_type")

    with pytest.raises(ValueError):
        await handler.handle(query)


@pytest.mark.asyncio
async def test_list_reports_by_status_with_invalid_status(test_session):
    """Test ListReportsByStatusHandler with invalid status"""
    repository = SQLAlchemyReportRepository(test_session)
    handler = ListReportsByStatusHandler(repository)

    query = ListReportsByStatusQuery(status="invalid_status")

    with pytest.raises(ValueError):
        await handler.handle(query)


@pytest.mark.asyncio
async def test_list_reports_by_status_filters_correctly(test_session):
    """Test ListReportsByStatusHandler returns only reports with matching status"""
    repository = SQLAlchemyReportRepository(test_session)
    handler = ListReportsByStatusHandler(repository)

    # Create reports with different statuses
    params = ReportParameters()

    # Create pending report
    pending_report = Report(
        name="Pending Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        parameters=params,
    )
    await repository.save(pending_report)

    # Create completed report
    completed_report = Report(
        name="Completed Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        parameters=params,
    )
    completed_report.start_processing()
    completed_report.complete("/app/reports/test.pdf")
    await repository.save(completed_report)

    await test_session.commit()

    # Query for pending reports only
    query = ListReportsByStatusQuery(status="pending")
    pending_reports = await handler.handle(query)

    assert len(pending_reports) == 1
    assert pending_reports[0].id == pending_report.id
    assert pending_reports[0].status == ReportStatus.PENDING


@pytest.mark.asyncio
async def test_list_reports_by_type_filters_correctly(test_session):
    """Test ListReportsByTypeHandler returns only reports with matching type"""
    repository = SQLAlchemyReportRepository(test_session)
    handler = ListReportsByTypeHandler(repository)

    params = ReportParameters()

    # Create payroll summary report
    payroll_report = Report(
        name="Payroll Report",
        report_type=ReportType.PAYROLL_SUMMARY,
        format=ReportFormat.PDF,
        parameters=params,
    )
    await repository.save(payroll_report)

    # Create tax report
    tax_report = Report(
        name="Tax Report",
        report_type=ReportType.TAX_REPORT,
        format=ReportFormat.PDF,
        parameters=params,
    )
    await repository.save(tax_report)

    await test_session.commit()

    # Query for payroll_summary reports only
    query = ListReportsByTypeQuery(report_type="payroll_summary")
    payroll_reports = await handler.handle(query)

    assert len(payroll_reports) == 1
    assert payroll_reports[0].id == payroll_report.id
    assert payroll_reports[0].report_type == ReportType.PAYROLL_SUMMARY
