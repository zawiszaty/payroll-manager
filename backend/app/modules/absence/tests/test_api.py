from decimal import Decimal
from uuid import uuid4

import pytest

from app.modules.absence.domain.value_objects import AbsenceType


@pytest.mark.asyncio
async def test_create_absence(client):
    employee_id = str(uuid4())

    response = await client.post(
        "/api/v1/absence/absences/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "start_date": "2025-06-01",
            "end_date": "2025-06-10",
            "reason": "Summer vacation",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["employee_id"] == employee_id
    assert data["absence_type"] == AbsenceType.VACATION.value
    assert data["status"] == "pending"
    assert data["reason"] == "Summer vacation"


@pytest.mark.asyncio
async def test_get_absence(client):
    employee_id = str(uuid4())

    create_response = await client.post(
        "/api/v1/absence/absences/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "start_date": "2025-06-01",
            "end_date": "2025-06-10",
        },
    )
    absence_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/absence/absences/{absence_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == absence_id
    assert data["employee_id"] == employee_id


@pytest.mark.asyncio
async def test_list_absences(client):
    response = await client.get("/api/v1/absence/absences/")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "metadata" in data
    assert "_links" in data
    assert "total_items" in data["metadata"]
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_absences_by_employee(client):
    employee_id = str(uuid4())

    await client.post(
        "/api/v1/absence/absences/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "start_date": "2025-06-01",
            "end_date": "2025-06-10",
        },
    )

    await client.post(
        "/api/v1/absence/absences/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.SICK_LEAVE.value,
            "start_date": "2025-07-01",
            "end_date": "2025-07-03",
        },
    )

    response = await client.get(f"/api/v1/absence/absences/employee/{employee_id}")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert all(a["employee_id"] == employee_id for a in data["items"])


@pytest.mark.asyncio
async def test_approve_absence(client):
    employee_id = str(uuid4())

    create_response = await client.post(
        "/api/v1/absence/absences/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "start_date": "2025-06-01",
            "end_date": "2025-06-10",
        },
    )
    absence_id = create_response.json()["id"]

    response = await client.post(f"/api/v1/absence/absences/{absence_id}/approve")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


@pytest.mark.asyncio
async def test_reject_absence(client):
    employee_id = str(uuid4())

    create_response = await client.post(
        "/api/v1/absence/absences/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "start_date": "2025-06-01",
            "end_date": "2025-06-10",
        },
    )
    absence_id = create_response.json()["id"]

    response = await client.post(f"/api/v1/absence/absences/{absence_id}/reject")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"


@pytest.mark.asyncio
async def test_cancel_absence(client):
    employee_id = str(uuid4())

    create_response = await client.post(
        "/api/v1/absence/absences/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "start_date": "2025-06-01",
            "end_date": "2025-06-10",
        },
    )
    absence_id = create_response.json()["id"]

    response = await client.post(f"/api/v1/absence/absences/{absence_id}/cancel")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_create_absence_balance(client):
    employee_id = str(uuid4())

    response = await client.post(
        "/api/v1/absence/balances/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "year": 2025,
            "total_days": "20.00",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["employee_id"] == employee_id
    assert data["absence_type"] == AbsenceType.VACATION.value
    assert data["year"] == 2025
    assert Decimal(data["total_days"]) == Decimal("20.00")
    assert Decimal(data["used_days"]) == Decimal("0.00")


@pytest.mark.asyncio
async def test_get_absence_balance(client):
    employee_id = str(uuid4())

    create_response = await client.post(
        "/api/v1/absence/balances/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "year": 2025,
            "total_days": "20.00",
        },
    )
    balance_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/absence/balances/{balance_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == balance_id
    assert data["employee_id"] == employee_id
    assert "remaining_days" in data


@pytest.mark.asyncio
async def test_list_absence_balances(client):
    response = await client.get("/api/v1/absence/balances/")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "metadata" in data
    assert "_links" in data
    assert "total_items" in data["metadata"]
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_absence_balances_by_employee(client):
    employee_id = str(uuid4())

    await client.post(
        "/api/v1/absence/balances/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "year": 2025,
            "total_days": "20.00",
        },
    )

    await client.post(
        "/api/v1/absence/balances/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.SICK_LEAVE.value,
            "year": 2025,
            "total_days": "10.00",
        },
    )

    response = await client.get(f"/api/v1/absence/balances/employee/{employee_id}")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert all(b["employee_id"] == employee_id for b in data["items"])


@pytest.mark.asyncio
async def test_get_absence_balances_by_employee_and_year(client):
    employee_id = str(uuid4())

    await client.post(
        "/api/v1/absence/balances/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "year": 2025,
            "total_days": "20.00",
        },
    )

    response = await client.get(f"/api/v1/absence/balances/employee/{employee_id}/year/2025")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["year"] == 2025


@pytest.mark.asyncio
async def test_update_absence_balance(client):
    employee_id = str(uuid4())

    create_response = await client.post(
        "/api/v1/absence/balances/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "year": 2025,
            "total_days": "20.00",
        },
    )
    balance_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/absence/balances/{balance_id}",
        json={"total_days": "25.00"},
    )

    assert response.status_code == 200
    data = response.json()
    assert Decimal(data["total_days"]) == Decimal("25.00")


@pytest.mark.asyncio
async def test_approve_absence_with_balance_deduction(client):
    employee_id = str(uuid4())

    await client.post(
        "/api/v1/absence/balances/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "year": 2025,
            "total_days": "20.00",
        },
    )

    create_response = await client.post(
        "/api/v1/absence/absences/",
        json={
            "employee_id": employee_id,
            "absence_type": AbsenceType.VACATION.value,
            "start_date": "2025-06-01",
            "end_date": "2025-06-10",
        },
    )
    absence_id = create_response.json()["id"]

    await client.post(f"/api/v1/absence/absences/{absence_id}/approve")

    balance_response = await client.get(
        f"/api/v1/absence/balances/employee/{employee_id}/year/2025"
    )
    balance_data = balance_response.json()["items"][0]

    assert Decimal(balance_data["used_days"]) == Decimal("10.00")
    assert Decimal(balance_data["remaining_days"]) == Decimal("10.00")
