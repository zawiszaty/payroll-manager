from uuid import uuid4

import pytest

from app.modules.audit.domain.models import AuditLog
from app.modules.audit.domain.value_objects import AuditAction, EntityType


@pytest.fixture
def sample_entity_id():
    return uuid4()


@pytest.fixture
def sample_employee_id():
    return uuid4()


@pytest.fixture
def sample_changed_by_id():
    return uuid4()


@pytest.fixture
def sample_audit_log(sample_entity_id, sample_employee_id):
    return AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=sample_entity_id,
        action=AuditAction.CREATED,
        employee_id=sample_employee_id,
        new_values={"first_name": "John", "last_name": "Doe"},
        metadata={"source": "system"},
    )


@pytest.fixture
def sample_contract_audit_log(sample_entity_id, sample_employee_id):
    return AuditLog.create(
        entity_type=EntityType.CONTRACT,
        entity_id=sample_entity_id,
        action=AuditAction.ACTIVATED,
        employee_id=sample_employee_id,
        old_values={"status": "pending"},
        new_values={"status": "active"},
    )


@pytest.fixture
def sample_payroll_audit_log(sample_entity_id, sample_employee_id):
    return AuditLog.create(
        entity_type=EntityType.PAYROLL,
        entity_id=sample_entity_id,
        action=AuditAction.CALCULATED,
        employee_id=sample_employee_id,
        new_values={"gross_pay": "5000.00", "net_pay": "4000.00"},
    )
