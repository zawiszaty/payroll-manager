from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_timesheet(async_client: AsyncClient):
    employee_id = uuid4()
    response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
            "overtime_hours": 0.0,
            "overtime_type": None,
            "project_id": None,
            "task_description": None,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["employee_id"] == str(employee_id)
    assert data["work_date"] == "2024-01-15"
    assert data["hours"] == 8.0
    assert data["overtime_hours"] == 0.0
    assert data["status"] == "draft"
    assert data["total_hours"] == 8.0


@pytest.mark.asyncio
async def test_create_timesheet_with_overtime(async_client: AsyncClient):
    employee_id = uuid4()
    response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
            "overtime_hours": 2.0,
            "overtime_type": "regular",
            "project_id": None,
            "task_description": "Backend development",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["hours"] == 8.0
    assert data["overtime_hours"] == 2.0
    assert data["overtime_type"] == "regular"
    assert data["total_hours"] == 10.0
    assert data["task_description"] == "Backend development"


@pytest.mark.asyncio
async def test_create_timesheet_invalid_overtime(async_client: AsyncClient):
    employee_id = uuid4()
    response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
            "overtime_hours": 2.0,
            "overtime_type": None,
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_timesheet(async_client: AsyncClient):
    employee_id = uuid4()
    create_response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    timesheet_id = create_response.json()["id"]

    response = await async_client.get(f"/api/v1/timesheet/{timesheet_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == timesheet_id
    assert data["employee_id"] == str(employee_id)


@pytest.mark.asyncio
async def test_get_timesheet_not_found(async_client: AsyncClient):
    non_existent_id = uuid4()
    response = await async_client.get(f"/api/v1/timesheet/{non_existent_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_timesheets(async_client: AsyncClient):
    employee_id = uuid4()
    await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-16",
            "hours": 7.5,
        },
    )

    response = await async_client.get("/api/v1/timesheet/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_timesheets_by_employee(async_client: AsyncClient):
    employee_id = uuid4()
    await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-16",
            "hours": 7.5,
        },
    )

    response = await async_client.get(f"/api/v1/timesheet/employee/{employee_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(ts["employee_id"] == str(employee_id) for ts in data)


@pytest.mark.asyncio
async def test_get_timesheets_by_employee_and_date_range(async_client: AsyncClient):
    employee_id = uuid4()
    await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-20",
            "hours": 7.5,
        },
    )

    response = await async_client.get(
        f"/api/v1/timesheet/employee/{employee_id}/period?start_date=2024-01-15&end_date=2024-01-15"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["work_date"] == "2024-01-15"


@pytest.mark.asyncio
async def test_update_timesheet(async_client: AsyncClient):
    employee_id = uuid4()
    create_response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    timesheet_id = create_response.json()["id"]

    response = await async_client.put(
        f"/api/v1/timesheet/{timesheet_id}",
        json={
            "hours": 7.0,
            "overtime_hours": 1.0,
            "overtime_type": "regular",
            "task_description": "Updated task",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["hours"] == 7.0
    assert data["overtime_hours"] == 1.0
    assert data["task_description"] == "Updated task"


@pytest.mark.asyncio
async def test_submit_timesheet(async_client: AsyncClient):
    employee_id = uuid4()
    create_response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    timesheet_id = create_response.json()["id"]

    response = await async_client.post(f"/api/v1/timesheet/{timesheet_id}/submit")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "submitted"
    assert data["submitted_at"] is not None


@pytest.mark.asyncio
async def test_approve_timesheet(async_client: AsyncClient):
    employee_id = uuid4()
    approver_id = uuid4()
    create_response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    timesheet_id = create_response.json()["id"]

    await async_client.post(f"/api/v1/timesheet/{timesheet_id}/submit")

    response = await async_client.post(
        f"/api/v1/timesheet/{timesheet_id}/approve",
        json={"approved_by": str(approver_id)},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["approved_by"] == str(approver_id)
    assert data["approved_at"] is not None


@pytest.mark.asyncio
async def test_reject_timesheet(async_client: AsyncClient):
    employee_id = uuid4()
    create_response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    timesheet_id = create_response.json()["id"]

    await async_client.post(f"/api/v1/timesheet/{timesheet_id}/submit")

    response = await async_client.post(
        f"/api/v1/timesheet/{timesheet_id}/reject",
        json={"reason": "Hours do not match project requirements"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["rejection_reason"] == "Hours do not match project requirements"


@pytest.mark.asyncio
async def test_get_pending_approval(async_client: AsyncClient):
    employee_id = uuid4()
    create_response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    timesheet_id = create_response.json()["id"]

    await async_client.post(f"/api/v1/timesheet/{timesheet_id}/submit")

    response = await async_client.get("/api/v1/timesheet/pending-approval/list")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(ts["id"] == timesheet_id for ts in data)


@pytest.mark.asyncio
async def test_sum_hours_in_interval(async_client: AsyncClient):
    employee_id = uuid4()
    approver_id = uuid4()

    ts1_response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    ts1_id = ts1_response.json()["id"]
    await async_client.post(f"/api/v1/timesheet/{ts1_id}/submit")
    await async_client.post(
        f"/api/v1/timesheet/{ts1_id}/approve", json={"approved_by": str(approver_id)}
    )

    ts2_response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-16",
            "hours": 7.5,
            "overtime_hours": 1.5,
            "overtime_type": "regular",
        },
    )
    ts2_id = ts2_response.json()["id"]
    await async_client.post(f"/api/v1/timesheet/{ts2_id}/submit")
    await async_client.post(
        f"/api/v1/timesheet/{ts2_id}/approve", json={"approved_by": str(approver_id)}
    )

    response = await async_client.get(
        f"/api/v1/timesheet/employee/{employee_id}/hours-summary?start_date=2024-01-15&end_date=2024-01-16"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_hours"] == 17.0


@pytest.mark.asyncio
async def test_delete_timesheet(async_client: AsyncClient):
    employee_id = uuid4()
    create_response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    timesheet_id = create_response.json()["id"]

    response = await async_client.delete(f"/api/v1/timesheet/{timesheet_id}")

    assert response.status_code == 204

    get_response = await async_client.get(f"/api/v1/timesheet/{timesheet_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_cannot_delete_submitted_timesheet(async_client: AsyncClient):
    employee_id = uuid4()
    create_response = await async_client.post(
        "/api/v1/timesheet/",
        json={
            "employee_id": str(employee_id),
            "work_date": "2024-01-15",
            "hours": 8.0,
        },
    )
    timesheet_id = create_response.json()["id"]
    await async_client.post(f"/api/v1/timesheet/{timesheet_id}/submit")

    response = await async_client.delete(f"/api/v1/timesheet/{timesheet_id}")

    assert response.status_code == 400
