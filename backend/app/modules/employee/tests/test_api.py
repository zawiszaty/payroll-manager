import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_employee(client: AsyncClient):
    response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "hire_date": "2024-01-01",
            "phone": "+1234567890",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["email"] == "jane.smith@example.com"
    assert len(data["statuses"]) == 1
    assert data["statuses"][0]["status_type"] == "active"


@pytest.mark.asyncio
async def test_get_employee(client: AsyncClient):
    create_response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@example.com",
            "hire_date": "2024-01-01",
        },
    )
    employee_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/employees/{employee_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "bob.johnson@example.com"


@pytest.mark.asyncio
async def test_list_employees(client: AsyncClient):
    for i in range(3):
        await client.post(
            "/api/v1/employees/",
            json={
                "first_name": f"Employee{i}",
                "last_name": "Test",
                "email": f"employee{i}@example.com",
                "hire_date": "2024-01-01",
            },
        )

    response = await client.get("/api/v1/employees/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "metadata" in data
    assert "_links" in data
    assert "total_items" in data["metadata"]
    assert len(data["items"]) >= 3
    assert data["metadata"]["total_items"] >= 3


@pytest.mark.asyncio
async def test_update_employee(client: AsyncClient):
    create_response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Update",
            "last_name": "Test",
            "email": "update.test@example.com",
            "hire_date": "2024-01-01",
        },
    )
    employee_id = create_response.json()["id"]

    response = await client.put(
        f"/api/v1/employees/{employee_id}", json={"first_name": "Updated", "phone": "+9999999999"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["phone"] == "+9999999999"


@pytest.mark.asyncio
async def test_change_employee_status(client: AsyncClient):
    create_response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Status",
            "last_name": "Test",
            "email": "status.test@example.com",
            "hire_date": "2024-01-01",
        },
    )
    employee_id = create_response.json()["id"]

    response = await client.post(
        f"/api/v1/employees/{employee_id}/status",
        json={"new_status": "on_leave", "effective_date": "2024-06-01", "reason": "Vacation"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["statuses"]) == 2


@pytest.mark.asyncio
async def test_duplicate_email_rejected(client: AsyncClient):
    await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Duplicate",
            "last_name": "Test",
            "email": "duplicate@example.com",
            "hire_date": "2024-01-01",
        },
    )

    response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Another",
            "last_name": "Duplicate",
            "email": "duplicate@example.com",
            "hire_date": "2024-01-01",
        },
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
