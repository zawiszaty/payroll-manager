import pytest

from app.modules.reporting.domain.entities import Report
from app.modules.reporting.domain.value_objects import (
    ReportFormat,
    ReportParameters,
    ReportStatus,
    ReportType,
)


def test_create_report():
    report = Report(
        name="Monthly Payroll Report",
        report_type=ReportType.PAYROLL_SUMMARY,
        format=ReportFormat.PDF,
    )

    assert report.id is not None
    assert report.name == "Monthly Payroll Report"
    assert report.report_type == ReportType.PAYROLL_SUMMARY
    assert report.format == ReportFormat.PDF
    assert report.status == ReportStatus.PENDING
    assert report.file_path is None
    assert report.error_message is None


def test_start_processing():
    report = Report(
        name="Test Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.CSV,
    )

    report.start_processing()

    assert report.status == ReportStatus.PROCESSING


def test_start_processing_invalid_status():
    report = Report(
        name="Test Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.CSV,
        status=ReportStatus.COMPLETED,
    )

    with pytest.raises(ValueError, match="Cannot start processing"):
        report.start_processing()


def test_complete_report():
    report = Report(
        name="Test Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        status=ReportStatus.PROCESSING,
    )

    report.complete("/path/to/report.pdf")

    assert report.status == ReportStatus.COMPLETED
    assert report.file_path == "/path/to/report.pdf"
    assert report.completed_at is not None


def test_complete_report_invalid_status():
    report = Report(
        name="Test Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.PDF,
        status=ReportStatus.PENDING,
    )

    with pytest.raises(ValueError, match="Cannot complete report"):
        report.complete("/path/to/report.pdf")


def test_fail_report():
    report = Report(
        name="Test Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.JSON,
        status=ReportStatus.PROCESSING,
    )

    report.fail("Database connection failed")

    assert report.status == ReportStatus.FAILED
    assert report.error_message == "Database connection failed"
    assert report.completed_at is not None


def test_fail_report_from_pending():
    report = Report(
        name="Test Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.XLSX,
        status=ReportStatus.PENDING,
    )

    report.fail("Validation error")

    assert report.status == ReportStatus.FAILED
    assert report.error_message == "Validation error"


def test_fail_report_invalid_status():
    report = Report(
        name="Test Report",
        report_type=ReportType.CUSTOM,
        format=ReportFormat.CSV,
        status=ReportStatus.COMPLETED,
    )

    with pytest.raises(ValueError, match="Cannot fail report"):
        report.fail("Some error")


def test_report_status_checks():
    report = Report(
        name="Test Report",
        report_type=ReportType.TAX_REPORT,
        format=ReportFormat.PDF,
    )

    assert report.is_pending() is True
    assert report.is_processing() is False
    assert report.is_completed() is False
    assert report.is_failed() is False

    report.start_processing()
    assert report.is_processing() is True
    assert report.is_pending() is False

    report.complete("/path/to/file")
    assert report.is_completed() is True
    assert report.is_processing() is False


def test_report_parameters_validation():
    params = ReportParameters(
        employee_id="emp-123",
        department="Engineering",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    assert params.employee_id == "emp-123"
    assert params.department == "Engineering"
    assert params.start_date == "2024-01-01"
    assert params.end_date == "2024-01-31"


def test_report_parameters_invalid_date_range():
    with pytest.raises(ValueError, match="Start date must be before or equal"):
        ReportParameters(
            start_date="2024-01-31",
            end_date="2024-01-01",
        )
