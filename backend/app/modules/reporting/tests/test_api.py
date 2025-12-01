from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_create_report(client):
    response = await client.post(
        "/api/v1/reporting/",
        json={
            "name": "Monthly Payroll Report",
            "report_type": "payroll_summary",
            "format": "pdf",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Monthly Payroll Report"
    assert data["report_type"] == "payroll_summary"
    assert data["format"] == "pdf"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_create_report_invalid_type(client):
    response = await client.post(
        "/api/v1/reporting/",
        json={
            "name": "Test Report",
            "report_type": "invalid_type",
            "format": "pdf",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_report(client, test_session):
    from app.modules.reporting.application.commands import CreateReportCommand
    from app.modules.reporting.application.handlers import CreateReportHandler
    from app.modules.reporting.infrastructure.repository import (
        SQLAlchemyReportRepository,
    )

    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)
    command = CreateReportCommand(
        name="Test Report",
        report_type="custom",
        format="csv",
    )
    report = await handler.handle(command)
    await test_session.commit()

    response = await client.get(f"/api/v1/reporting/{report.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(report.id)
    assert data["name"] == "Test Report"


@pytest.mark.asyncio
async def test_get_report_not_found(client):
    response = await client.get(f"/api/v1/reporting/{uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_reports(client, test_session):
    from app.modules.reporting.application.commands import CreateReportCommand
    from app.modules.reporting.application.handlers import CreateReportHandler
    from app.modules.reporting.infrastructure.repository import (
        SQLAlchemyReportRepository,
    )

    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)

    for i in range(3):
        command = CreateReportCommand(
            name=f"Report {i}",
            report_type="custom",
            format="pdf",
        )
        await handler.handle(command)

    await test_session.commit()

    response = await client.get("/api/v1/reporting/")

    assert response.status_code == 200
    data = response.json()
    assert len(data["reports"]) == 3


@pytest.mark.asyncio
async def test_list_reports_by_type(client, test_session):
    from app.modules.reporting.application.commands import CreateReportCommand
    from app.modules.reporting.application.handlers import CreateReportHandler
    from app.modules.reporting.infrastructure.repository import (
        SQLAlchemyReportRepository,
    )

    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)

    command1 = CreateReportCommand(
        name="Payroll Report",
        report_type="payroll_summary",
        format="pdf",
    )
    await handler.handle(command1)

    command2 = CreateReportCommand(
        name="Tax Report",
        report_type="tax_report",
        format="pdf",
    )
    await handler.handle(command2)

    await test_session.commit()

    response = await client.get("/api/v1/reporting/type/payroll_summary")

    assert response.status_code == 200
    data = response.json()
    assert len(data["reports"]) == 1
    assert data["reports"][0]["report_type"] == "payroll_summary"


@pytest.mark.asyncio
async def test_list_reports_by_status(client, test_session):
    from app.modules.reporting.application.commands import CreateReportCommand
    from app.modules.reporting.application.handlers import CreateReportHandler
    from app.modules.reporting.infrastructure.repository import (
        SQLAlchemyReportRepository,
    )

    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)

    command = CreateReportCommand(
        name="Test Report",
        report_type="custom",
        format="pdf",
    )
    await handler.handle(command)
    await test_session.commit()

    response = await client.get("/api/v1/reporting/status/pending")

    assert response.status_code == 200
    data = response.json()
    assert len(data["reports"]) == 1
    assert data["reports"][0]["status"] == "pending"


@pytest.mark.asyncio
async def test_generate_report(client, test_session):
    from app.modules.reporting.application.commands import CreateReportCommand
    from app.modules.reporting.application.handlers import CreateReportHandler
    from app.modules.reporting.infrastructure.repository import (
        SQLAlchemyReportRepository,
    )

    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)
    command = CreateReportCommand(
        name="Test Report",
        report_type="payroll_summary",
        format="pdf",
    )
    report = await handler.handle(command)
    await test_session.commit()

    response = await client.post(f"/api/v1/reporting/{report.id}/generate")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["file_path"] is not None
    assert ".pdf" in data["file_path"]


@pytest.mark.asyncio
async def test_generate_report_csv(client, test_session):
    from app.modules.reporting.application.commands import CreateReportCommand
    from app.modules.reporting.application.handlers import CreateReportHandler
    from app.modules.reporting.infrastructure.repository import (
        SQLAlchemyReportRepository,
    )

    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)
    command = CreateReportCommand(
        name="CSV Report",
        report_type="employee_compensation",
        format="csv",
    )
    report = await handler.handle(command)
    await test_session.commit()

    response = await client.post(f"/api/v1/reporting/{report.id}/generate")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert ".csv" in data["file_path"]


@pytest.mark.asyncio
async def test_generate_already_completed_report(client, test_session):
    from app.modules.reporting.application.commands import CreateReportCommand
    from app.modules.reporting.application.handlers import CreateReportHandler
    from app.modules.reporting.infrastructure.repository import (
        SQLAlchemyReportRepository,
    )

    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)
    command = CreateReportCommand(
        name="Test Report",
        report_type="custom",
        format="json",
    )
    report = await handler.handle(command)
    await test_session.commit()

    await client.post(f"/api/v1/reporting/{report.id}/generate")
    response = await client.post(f"/api/v1/reporting/{report.id}/generate")

    assert response.status_code == 400
    assert "already generated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_download_report(client, test_session):
    from app.modules.reporting.application.commands import CreateReportCommand
    from app.modules.reporting.application.handlers import CreateReportHandler
    from app.modules.reporting.infrastructure.repository import (
        SQLAlchemyReportRepository,
    )

    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)
    command = CreateReportCommand(
        name="Download Test",
        report_type="payroll_summary",
        format="pdf",
    )
    report = await handler.handle(command)
    await test_session.commit()

    await client.post(f"/api/v1/reporting/{report.id}/generate")

    response = await client.get(f"/api/v1/reporting/{report.id}/download")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"


@pytest.mark.asyncio
async def test_download_not_generated_report(client, test_session):
    from app.modules.reporting.application.commands import CreateReportCommand
    from app.modules.reporting.application.handlers import CreateReportHandler
    from app.modules.reporting.infrastructure.repository import (
        SQLAlchemyReportRepository,
    )

    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)
    command = CreateReportCommand(
        name="Test Report",
        report_type="custom",
        format="pdf",
    )
    report = await handler.handle(command)
    await test_session.commit()

    response = await client.get(f"/api/v1/reporting/{report.id}/download")
    assert response.status_code == 400
    assert "not ready for download" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_report(client, test_session):
    from app.modules.reporting.application.commands import CreateReportCommand
    from app.modules.reporting.application.handlers import CreateReportHandler
    from app.modules.reporting.infrastructure.repository import (
        SQLAlchemyReportRepository,
    )

    repository = SQLAlchemyReportRepository(test_session)
    handler = CreateReportHandler(repository)
    command = CreateReportCommand(
        name="Test Report",
        report_type="custom",
        format="pdf",
    )
    report = await handler.handle(command)
    await test_session.commit()

    response = await client.delete(f"/api/v1/reporting/{report.id}")
    assert response.status_code == 204

    response = await client.get(f"/api/v1/reporting/{report.id}")
    assert response.status_code == 404
