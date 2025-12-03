from uuid import uuid4

import pytest

from app.modules.audit.domain.models import AuditLog
from app.modules.audit.domain.value_objects import AuditAction, EntityType
from app.modules.audit.infrastructure.repository import SQLAlchemyAuditLogRepository


@pytest.mark.asyncio
async def test_list_audit_logs(client, test_session):
    repository = SQLAlchemyAuditLogRepository(test_session)

    entity_id = uuid4()
    employee_id = uuid4()

    audit_log1 = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=entity_id,
        action=AuditAction.CREATED,
        employee_id=employee_id,
    )
    audit_log2 = AuditLog.create(
        entity_type=EntityType.CONTRACT,
        entity_id=uuid4(),
        action=AuditAction.ACTIVATED,
        employee_id=employee_id,
    )

    await repository.save(audit_log1)
    await repository.save(audit_log2)

    response = await client.get("/api/v1/audit/")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_get_audit_log_by_id(client, test_session):
    repository = SQLAlchemyAuditLogRepository(test_session)

    entity_id = uuid4()
    audit_log = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=entity_id,
        action=AuditAction.CREATED,
        new_values={"first_name": "John", "last_name": "Doe"},
    )

    saved_log = await repository.save(audit_log)

    response = await client.get(f"/api/v1/audit/{saved_log.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(saved_log.id)
    assert data["entity_type"] == EntityType.EMPLOYEE.value
    assert data["entity_id"] == str(entity_id)
    assert data["action"] == AuditAction.CREATED.value
    assert data["new_values"]["first_name"] == "John"


@pytest.mark.asyncio
async def test_get_audit_log_not_found(client):
    non_existent_id = uuid4()
    response = await client.get(f"/api/v1/audit/{non_existent_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_audit_logs_filtered_by_entity_type(client, test_session):
    repository = SQLAlchemyAuditLogRepository(test_session)

    employee_log = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=uuid4(),
        action=AuditAction.CREATED,
    )
    contract_log = AuditLog.create(
        entity_type=EntityType.CONTRACT,
        entity_id=uuid4(),
        action=AuditAction.ACTIVATED,
    )

    await repository.save(employee_log)
    await repository.save(contract_log)

    response = await client.get("/api/v1/audit/?entity_type=employee")

    assert response.status_code == 200
    data = response.json()
    assert all(item["entity_type"] == "employee" for item in data["items"])


@pytest.mark.asyncio
async def test_list_audit_logs_filtered_by_action(client, test_session):
    repository = SQLAlchemyAuditLogRepository(test_session)

    created_log = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=uuid4(),
        action=AuditAction.CREATED,
    )
    updated_log = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=uuid4(),
        action=AuditAction.UPDATED,
    )

    await repository.save(created_log)
    await repository.save(updated_log)

    response = await client.get("/api/v1/audit/?action=created")

    assert response.status_code == 200
    data = response.json()
    assert all(item["action"] == "created" for item in data["items"])


@pytest.mark.asyncio
async def test_list_audit_logs_invalid_entity_type(client):
    response = await client.get("/api/v1/audit/?entity_type=invalid_type")

    assert response.status_code == 400
    assert "Invalid entity_type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_audit_logs_invalid_action(client):
    response = await client.get("/api/v1/audit/?action=invalid_action")

    assert response.status_code == 400
    assert "Invalid action" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_audit_logs_by_entity(client, test_session):
    repository = SQLAlchemyAuditLogRepository(test_session)

    entity_id = uuid4()

    created_log = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=entity_id,
        action=AuditAction.CREATED,
    )
    updated_log = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=entity_id,
        action=AuditAction.UPDATED,
    )

    other_entity_log = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=uuid4(),
        action=AuditAction.CREATED,
    )

    await repository.save(created_log)
    await repository.save(updated_log)
    await repository.save(other_entity_log)

    response = await client.get(f"/api/v1/audit/entity/employee/{entity_id}")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 2
    assert all(item["entity_id"] == str(entity_id) for item in data["items"])


@pytest.mark.asyncio
async def test_get_audit_logs_by_entity_invalid_type(client):
    entity_id = uuid4()
    response = await client.get(f"/api/v1/audit/entity/invalid_type/{entity_id}")

    assert response.status_code == 400
    assert "Invalid entity type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_audit_logs_by_employee(client, test_session):
    repository = SQLAlchemyAuditLogRepository(test_session)

    employee_id = uuid4()

    log1 = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=uuid4(),
        action=AuditAction.CREATED,
        employee_id=employee_id,
    )
    log2 = AuditLog.create(
        entity_type=EntityType.CONTRACT,
        entity_id=uuid4(),
        action=AuditAction.ACTIVATED,
        employee_id=employee_id,
    )

    other_employee_log = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=uuid4(),
        action=AuditAction.CREATED,
        employee_id=uuid4(),
    )

    await repository.save(log1)
    await repository.save(log2)
    await repository.save(other_employee_log)

    response = await client.get(f"/api/v1/audit/employee/{employee_id}")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 2
    assert all(item["employee_id"] == str(employee_id) for item in data["items"])


@pytest.mark.asyncio
async def test_get_audit_timeline(client, test_session):
    repository = SQLAlchemyAuditLogRepository(test_session)

    log1 = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=uuid4(),
        action=AuditAction.CREATED,
    )
    log2 = AuditLog.create(
        entity_type=EntityType.PAYROLL,
        entity_id=uuid4(),
        action=AuditAction.CALCULATED,
    )

    await repository.save(log1)
    await repository.save(log2)

    response = await client.get("/api/v1/audit/timeline")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 2


@pytest.mark.asyncio
async def test_get_audit_timeline_filtered(client, test_session):
    repository = SQLAlchemyAuditLogRepository(test_session)

    employee_id = uuid4()

    log1 = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=uuid4(),
        action=AuditAction.CREATED,
        employee_id=employee_id,
    )
    log2 = AuditLog.create(
        entity_type=EntityType.CONTRACT,
        entity_id=uuid4(),
        action=AuditAction.ACTIVATED,
        employee_id=uuid4(),
    )

    await repository.save(log1)
    await repository.save(log2)

    response = await client.get(f"/api/v1/audit/timeline?employee_id={employee_id}")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert all(
        item.get("employee_id") == str(employee_id)
        for item in data["items"]
        if item.get("employee_id")
    )


@pytest.mark.asyncio
async def test_list_audit_logs_with_pagination(client, test_session):
    repository = SQLAlchemyAuditLogRepository(test_session)

    for _ in range(5):
        log = AuditLog.create(
            entity_type=EntityType.EMPLOYEE,
            entity_id=uuid4(),
            action=AuditAction.CREATED,
        )
        await repository.save(log)

    response = await client.get("/api/v1/audit/?page=1&limit=2")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["items"]) <= 2
