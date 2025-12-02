"""Tests for reporting repository"""

import pytest

from app.modules.reporting.domain.entities import Report
from app.modules.reporting.domain.value_objects import (
    ReportFormat,
    ReportParameters,
    ReportStatus,
    ReportType,
)
from app.modules.reporting.infrastructure.repository import SQLAlchemyReportRepository


@pytest.mark.asyncio
async def test_repository_save_and_get_by_id(test_session):
    """Test saving and retrieving a report"""
    repository = SQLAlchemyReportRepository(test_session)

    params = ReportParameters()
    report = Report(
        name="Test Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        parameters=params,
    )

    saved_report = await repository.save(report)
    await test_session.commit()

    retrieved = await repository.get_by_id(saved_report.id)

    assert retrieved is not None
    assert retrieved.id == saved_report.id
    assert retrieved.name == "Test Report"


@pytest.mark.asyncio
async def test_repository_get_by_id_not_found(test_session):
    """Test get_by_id returns None for non-existent report"""
    from uuid import uuid4

    repository = SQLAlchemyReportRepository(test_session)

    result = await repository.get_by_id(uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_repository_update(test_session):
    """Test updating a report"""
    repository = SQLAlchemyReportRepository(test_session)

    params = ReportParameters()
    report = Report(
        name="Original Name",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        parameters=params,
    )

    await repository.save(report)
    await test_session.commit()

    # Start processing
    report.start_processing()
    await repository.save(report)
    await test_session.commit()

    # Retrieve and verify
    updated = await repository.get_by_id(report.id)
    assert updated.status == ReportStatus.PROCESSING


@pytest.mark.asyncio
async def test_repository_delete(test_session):
    """Test deleting a report"""
    repository = SQLAlchemyReportRepository(test_session)

    params = ReportParameters()
    report = Report(
        name="To Delete",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        parameters=params,
    )

    await repository.save(report)
    await test_session.commit()

    # Delete
    await repository.delete(report.id)
    await test_session.commit()

    # Verify deleted
    deleted = await repository.get_by_id(report.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_repository_delete_nonexistent(test_session):
    """Test deleting a non-existent report (should not raise error)"""
    from uuid import uuid4

    repository = SQLAlchemyReportRepository(test_session)

    # Should not raise an error even if report doesn't exist
    await repository.delete(uuid4())
    await test_session.commit()


@pytest.mark.asyncio
async def test_repository_list_all(test_session):
    """Test listing all reports"""
    repository = SQLAlchemyReportRepository(test_session)

    params = ReportParameters()

    # Create multiple reports
    for i in range(3):
        report = Report(
            name=f"Report {i}",
            report_type=ReportType.CUSTOM,
            format=ReportFormat.PDF,
            parameters=params,
        )
        await repository.save(report)

    await test_session.commit()

    all_reports = await repository.list_all()

    assert len(all_reports) == 3


@pytest.mark.asyncio
async def test_repository_list_by_type(test_session):
    """Test listing reports by type"""
    repository = SQLAlchemyReportRepository(test_session)

    params = ReportParameters()

    # Create reports of different types
    payroll_report = Report(
        name="Payroll Report",
        report_type=ReportType.PAYROLL_SUMMARY,
        format=ReportFormat.PDF,
        parameters=params,
    )
    await repository.save(payroll_report)

    tax_report = Report(
        name="Tax Report",
        report_type=ReportType.TAX_REPORT,
        format=ReportFormat.PDF,
        parameters=params,
    )
    await repository.save(tax_report)

    custom_report = Report(
        name="Custom Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        parameters=params,
    )
    await repository.save(custom_report)

    await test_session.commit()

    # List payroll reports
    payroll_reports = await repository.list_by_type(ReportType.PAYROLL_SUMMARY)
    assert len(payroll_reports) == 1
    assert payroll_reports[0].report_type == ReportType.PAYROLL_SUMMARY

    # List tax reports
    tax_reports = await repository.list_by_type(ReportType.TAX_REPORT)
    assert len(tax_reports) == 1
    assert tax_reports[0].report_type == ReportType.TAX_REPORT


@pytest.mark.asyncio
async def test_repository_list_by_status(test_session):
    """Test listing reports by status"""
    repository = SQLAlchemyReportRepository(test_session)

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

    # Create failed report
    failed_report = Report(
        name="Failed Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        parameters=params,
    )
    failed_report.start_processing()
    failed_report.fail("Test error")
    await repository.save(failed_report)

    await test_session.commit()

    # List pending reports
    pending_reports = await repository.list_by_status(ReportStatus.PENDING)
    assert len(pending_reports) == 1
    assert pending_reports[0].status == ReportStatus.PENDING

    # List completed reports
    completed_reports = await repository.list_by_status(ReportStatus.COMPLETED)
    assert len(completed_reports) == 1
    assert completed_reports[0].status == ReportStatus.COMPLETED

    # List failed reports
    failed_reports = await repository.list_by_status(ReportStatus.FAILED)
    assert len(failed_reports) == 1
    assert failed_reports[0].status == ReportStatus.FAILED


@pytest.mark.asyncio
async def test_repository_update_with_parameters(test_session):
    """Test updating a report preserves all parameters"""
    from datetime import date

    repository = SQLAlchemyReportRepository(test_session)

    params = ReportParameters(
        department="Engineering",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        additional_filters={"key": "value"},
    )

    report = Report(
        name="Test Report",
        report_type=ReportType.PAYROLL_SUMMARY,
        format=ReportFormat.CSV,
        parameters=params,
    )

    await repository.save(report)
    await test_session.commit()

    # Update the report
    report.start_processing()
    report.complete("/app/reports/test.csv")
    await repository.save(report)
    await test_session.commit()

    # Retrieve and verify all fields preserved
    updated = await repository.get_by_id(report.id)
    assert updated.status == ReportStatus.COMPLETED
    assert updated.file_path == "/app/reports/test.csv"
    assert updated.parameters.department == "Engineering"
    assert updated.parameters.start_date == date(2024, 1, 1)
    assert updated.parameters.end_date == date(2024, 1, 31)
    assert updated.parameters.additional_filters == {"key": "value"}
