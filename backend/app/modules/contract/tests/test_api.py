
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_contract(client: AsyncClient):
    employee_response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "hire_date": "2024-01-01",
        },
    )
    employee_id = employee_response.json()["id"]

    response = await client.post(
        "/api/v1/contracts/",
        json={
            "employee_id": employee_id,
            "contract_type": "fixed_monthly",
            "rate_amount": "5000.00",
            "rate_currency": "USD",
            "valid_from": "2024-01-01",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["employee_id"] == employee_id
    assert data["status"] == "pending"
    assert data["terms"]["contract_type"] == "fixed_monthly"
    assert data["terms"]["rate_amount"] == "5000.00"


@pytest.mark.asyncio
async def test_get_contract(client: AsyncClient):
    employee_response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "hire_date": "2024-01-01",
        },
    )
    employee_id = employee_response.json()["id"]

    create_response = await client.post(
        "/api/v1/contracts/",
        json={
            "employee_id": employee_id,
            "contract_type": "hourly",
            "rate_amount": "50.00",
            "rate_currency": "USD",
            "valid_from": "2024-01-01",
            "hours_per_week": 40,
        },
    )
    contract_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/contracts/{contract_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contract_id
    assert data["terms"]["hours_per_week"] == 40


@pytest.mark.asyncio
async def test_activate_contract(client: AsyncClient):
    employee_response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@example.com",
            "hire_date": "2024-01-01",
        },
    )
    employee_id = employee_response.json()["id"]

    create_response = await client.post(
        "/api/v1/contracts/",
        json={
            "employee_id": employee_id,
            "contract_type": "fixed_monthly",
            "rate_amount": "6000.00",
            "rate_currency": "USD",
            "valid_from": "2024-01-01",
        },
    )
    contract_id = create_response.json()["id"]

    response = await client.post(f"/api/v1/contracts/{contract_id}/activate")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_cancel_contract(client: AsyncClient):
    employee_response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Alice",
            "last_name": "Williams",
            "email": "alice.williams@example.com",
            "hire_date": "2024-01-01",
        },
    )
    employee_id = employee_response.json()["id"]

    create_response = await client.post(
        "/api/v1/contracts/",
        json={
            "employee_id": employee_id,
            "contract_type": "fixed_monthly",
            "rate_amount": "7000.00",
            "rate_currency": "USD",
            "valid_from": "2024-01-01",
        },
    )
    contract_id = create_response.json()["id"]

    await client.post(f"/api/v1/contracts/{contract_id}/activate")

    response = await client.post(
        f"/api/v1/contracts/{contract_id}/cancel", json={"reason": "Project ended"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "canceled"
    assert data["cancellation_reason"] == "Project ended"


@pytest.mark.asyncio
async def test_get_contracts_by_employee(client: AsyncClient):
    employee_response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie.brown@example.com",
            "hire_date": "2024-01-01",
        },
    )
    employee_id = employee_response.json()["id"]

    for i in range(3):
        await client.post(
            "/api/v1/contracts/",
            json={
                "employee_id": employee_id,
                "contract_type": "fixed_monthly",
                "rate_amount": f"{5000 + i * 1000}.00",
                "rate_currency": "USD",
                "valid_from": "2024-01-01",
            },
        )

    response = await client.get(f"/api/v1/contracts/employee/{employee_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_hourly_contract_validation(client: AsyncClient):
    employee_response = await client.post(
        "/api/v1/employees/",
        json={
            "first_name": "David",
            "last_name": "Miller",
            "email": "david.miller@example.com",
            "hire_date": "2024-01-01",
        },
    )
    employee_id = employee_response.json()["id"]

    response = await client.post(
        "/api/v1/contracts/",
        json={
            "employee_id": employee_id,
            "contract_type": "hourly",
            "rate_amount": "50.00",
            "rate_currency": "USD",
            "valid_from": "2024-01-01",
        },
    )

    assert response.status_code == 400
    assert "hours_per_week" in response.json()["detail"]
