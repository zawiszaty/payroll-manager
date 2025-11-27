from decimal import Decimal
from uuid import uuid4

import pytest

from app.modules.compensation.domain.value_objects import BonusType, RateType


@pytest.mark.asyncio
async def test_create_rate(client):
    employee_id = str(uuid4())

    response = await client.post(
        "/api/v1/compensation/rates/",
        json={
            "employee_id": employee_id,
            "rate_type": RateType.HOURLY_RATE.value,
            "amount": "25.00",
            "currency": "USD",
            "valid_from": "2025-01-01",
            "valid_to": "2025-12-31",
            "description": "Hourly rate for developer",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["employee_id"] == employee_id
    assert data["rate_type"] == RateType.HOURLY_RATE.value
    assert Decimal(data["amount"]) == Decimal("25.00")
    assert data["currency"] == "USD"
    assert data["description"] == "Hourly rate for developer"


@pytest.mark.asyncio
async def test_get_rate(client):
    employee_id = str(uuid4())

    create_response = await client.post(
        "/api/v1/compensation/rates/",
        json={
            "employee_id": employee_id,
            "rate_type": RateType.BASE_SALARY.value,
            "amount": "5000.00",
            "currency": "USD",
            "valid_from": "2025-01-01",
        },
    )
    rate_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/compensation/rates/{rate_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rate_id
    assert data["employee_id"] == employee_id


@pytest.mark.asyncio
async def test_list_rates(client):
    response = await client.get("/api/v1/compensation/rates/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_rates_by_employee(client):
    employee_id = str(uuid4())

    await client.post(
        "/api/v1/compensation/rates/",
        json={
            "employee_id": employee_id,
            "rate_type": RateType.HOURLY_RATE.value,
            "amount": "25.00",
            "currency": "USD",
            "valid_from": "2025-01-01",
        },
    )

    await client.post(
        "/api/v1/compensation/rates/",
        json={
            "employee_id": employee_id,
            "rate_type": RateType.BASE_SALARY.value,
            "amount": "4000.00",
            "currency": "USD",
            "valid_from": "2025-06-01",
        },
    )

    response = await client.get(f"/api/v1/compensation/rates/employee/{employee_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(r["employee_id"] == employee_id for r in data)


@pytest.mark.asyncio
async def test_get_active_rate(client):
    employee_id = str(uuid4())

    await client.post(
        "/api/v1/compensation/rates/",
        json={
            "employee_id": employee_id,
            "rate_type": RateType.HOURLY_RATE.value,
            "amount": "25.00",
            "currency": "USD",
            "valid_from": "2025-01-01",
            "valid_to": "2025-05-31",
        },
    )

    await client.post(
        "/api/v1/compensation/rates/",
        json={
            "employee_id": employee_id,
            "rate_type": RateType.BASE_SALARY.value,
            "amount": "5000.00",
            "currency": "USD",
            "valid_from": "2025-06-01",
        },
    )

    response = await client.get(
        f"/api/v1/compensation/rates/employee/{employee_id}/active",
        params={"check_date": "2025-06-15"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == employee_id
    assert data["rate_type"] == RateType.BASE_SALARY.value
    assert Decimal(data["amount"]) == Decimal("5000.00")


@pytest.mark.asyncio
async def test_create_bonus(client):
    employee_id = str(uuid4())

    response = await client.post(
        "/api/v1/compensation/bonuses/",
        json={
            "employee_id": employee_id,
            "bonus_type": BonusType.PERFORMANCE.value,
            "amount": "1000.00",
            "currency": "USD",
            "payment_date": "2025-06-30",
            "description": "Q2 performance bonus",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["employee_id"] == employee_id
    assert data["bonus_type"] == BonusType.PERFORMANCE.value
    assert Decimal(data["amount"]) == Decimal("1000.00")
    assert data["description"] == "Q2 performance bonus"


@pytest.mark.asyncio
async def test_get_bonus(client):
    employee_id = str(uuid4())

    create_response = await client.post(
        "/api/v1/compensation/bonuses/",
        json={
            "employee_id": employee_id,
            "bonus_type": BonusType.ANNUAL.value,
            "amount": "2000.00",
            "currency": "USD",
            "payment_date": "2025-12-31",
        },
    )
    bonus_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/compensation/bonuses/{bonus_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == bonus_id
    assert data["employee_id"] == employee_id


@pytest.mark.asyncio
async def test_list_bonuses(client):
    response = await client.get("/api/v1/compensation/bonuses/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_bonuses_by_employee(client):
    employee_id = str(uuid4())

    await client.post(
        "/api/v1/compensation/bonuses/",
        json={
            "employee_id": employee_id,
            "bonus_type": BonusType.PERFORMANCE.value,
            "amount": "1000.00",
            "currency": "USD",
            "payment_date": "2025-06-30",
        },
    )

    await client.post(
        "/api/v1/compensation/bonuses/",
        json={
            "employee_id": employee_id,
            "bonus_type": BonusType.HOLIDAY.value,
            "amount": "500.00",
            "currency": "USD",
            "payment_date": "2025-12-25",
        },
    )

    response = await client.get(f"/api/v1/compensation/bonuses/employee/{employee_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(b["employee_id"] == employee_id for b in data)
