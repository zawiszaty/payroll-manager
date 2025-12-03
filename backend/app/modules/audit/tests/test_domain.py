from datetime import UTC, datetime
from uuid import uuid4

from app.modules.audit.domain.models import AuditLog
from app.modules.audit.domain.value_objects import AuditAction, EntityType


def test_audit_log_creation():
    entity_id = uuid4()
    employee_id = uuid4()

    audit_log = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=entity_id,
        action=AuditAction.CREATED,
        employee_id=employee_id,
    )

    assert audit_log.id is not None
    assert audit_log.entity_type == EntityType.EMPLOYEE
    assert audit_log.entity_id == entity_id
    assert audit_log.action == AuditAction.CREATED
    assert audit_log.employee_id == employee_id
    assert audit_log.old_values is None
    assert audit_log.new_values is None
    assert audit_log.metadata == {}
    assert audit_log.occurred_at is not None
    assert audit_log.created_at is not None


def test_audit_log_with_old_and_new_values():
    entity_id = uuid4()
    old_values = {"status": "active"}
    new_values = {"status": "terminated"}

    audit_log = AuditLog.create(
        entity_type=EntityType.EMPLOYEE,
        entity_id=entity_id,
        action=AuditAction.STATUS_CHANGED,
        old_values=old_values,
        new_values=new_values,
    )

    assert audit_log.old_values == old_values
    assert audit_log.new_values == new_values


def test_audit_log_with_metadata():
    entity_id = uuid4()
    metadata = {"reason": "End of contract", "source": "system"}

    audit_log = AuditLog.create(
        entity_type=EntityType.CONTRACT,
        entity_id=entity_id,
        action=AuditAction.EXPIRED,
        metadata=metadata,
    )

    assert audit_log.metadata == metadata


def test_audit_log_with_custom_occurred_at():
    entity_id = uuid4()
    custom_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)

    audit_log = AuditLog.create(
        entity_type=EntityType.PAYROLL,
        entity_id=entity_id,
        action=AuditAction.CALCULATED,
        occurred_at=custom_time,
    )

    assert audit_log.occurred_at == custom_time


def test_audit_log_with_changed_by():
    entity_id = uuid4()
    changed_by_id = uuid4()

    audit_log = AuditLog.create(
        entity_type=EntityType.ABSENCE,
        entity_id=entity_id,
        action=AuditAction.APPROVED,
        changed_by=changed_by_id,
    )

    assert audit_log.changed_by == changed_by_id


def test_audit_log_for_contract_actions():
    entity_id = uuid4()

    created_log = AuditLog.create(
        entity_type=EntityType.CONTRACT, entity_id=entity_id, action=AuditAction.CREATED
    )
    assert created_log.action == AuditAction.CREATED

    activated_log = AuditLog.create(
        entity_type=EntityType.CONTRACT, entity_id=entity_id, action=AuditAction.ACTIVATED
    )
    assert activated_log.action == AuditAction.ACTIVATED

    canceled_log = AuditLog.create(
        entity_type=EntityType.CONTRACT, entity_id=entity_id, action=AuditAction.CANCELED
    )
    assert canceled_log.action == AuditAction.CANCELED

    expired_log = AuditLog.create(
        entity_type=EntityType.CONTRACT, entity_id=entity_id, action=AuditAction.EXPIRED
    )
    assert expired_log.action == AuditAction.EXPIRED


def test_audit_log_for_payroll_actions():
    entity_id = uuid4()

    calculated_log = AuditLog.create(
        entity_type=EntityType.PAYROLL, entity_id=entity_id, action=AuditAction.CALCULATED
    )
    assert calculated_log.action == AuditAction.CALCULATED

    approved_log = AuditLog.create(
        entity_type=EntityType.PAYROLL, entity_id=entity_id, action=AuditAction.APPROVED
    )
    assert approved_log.action == AuditAction.APPROVED

    processed_log = AuditLog.create(
        entity_type=EntityType.PAYROLL, entity_id=entity_id, action=AuditAction.PROCESSED
    )
    assert processed_log.action == AuditAction.PROCESSED

    paid_log = AuditLog.create(
        entity_type=EntityType.PAYROLL, entity_id=entity_id, action=AuditAction.PAID
    )
    assert paid_log.action == AuditAction.PAID


def test_audit_log_for_absence_actions():
    entity_id = uuid4()

    approved_log = AuditLog.create(
        entity_type=EntityType.ABSENCE, entity_id=entity_id, action=AuditAction.APPROVED
    )
    assert approved_log.action == AuditAction.APPROVED

    rejected_log = AuditLog.create(
        entity_type=EntityType.ABSENCE, entity_id=entity_id, action=AuditAction.REJECTED
    )
    assert rejected_log.action == AuditAction.REJECTED

    canceled_log = AuditLog.create(
        entity_type=EntityType.ABSENCE, entity_id=entity_id, action=AuditAction.CANCELED
    )
    assert canceled_log.action == AuditAction.CANCELED


def test_audit_log_for_report_actions():
    entity_id = uuid4()

    completed_log = AuditLog.create(
        entity_type=EntityType.REPORT, entity_id=entity_id, action=AuditAction.COMPLETED
    )
    assert completed_log.action == AuditAction.COMPLETED

    failed_log = AuditLog.create(
        entity_type=EntityType.REPORT, entity_id=entity_id, action=AuditAction.FAILED
    )
    assert failed_log.action == AuditAction.FAILED
