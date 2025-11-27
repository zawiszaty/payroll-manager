from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from app.modules.contract.domain.models import Contract
from app.modules.contract.domain.value_objects import ContractStatus, ContractTerms, ContractType
from app.shared.domain.value_objects import DateRange, Money


def test_contract_creation():
    employee_id = uuid4()
    terms = ContractTerms(
        contract_type=ContractType.FIXED_MONTHLY,
        rate=Money(amount=Decimal("5000.00"), currency="USD"),
        date_range=DateRange(valid_from=date(2024, 1, 1)),
    )
    contract = Contract(employee_id=employee_id, terms=terms)

    assert contract.employee_id == employee_id
    assert contract.status == ContractStatus.PENDING
    assert contract.terms.contract_type == ContractType.FIXED_MONTHLY


def test_contract_activate():
    employee_id = uuid4()
    terms = ContractTerms(
        contract_type=ContractType.FIXED_MONTHLY,
        rate=Money(amount=Decimal("5000.00"), currency="USD"),
        date_range=DateRange(valid_from=date(2024, 1, 1)),
    )
    contract = Contract(employee_id=employee_id, terms=terms)

    contract.activate()
    assert contract.status == ContractStatus.ACTIVE


def test_cannot_activate_active_contract():
    employee_id = uuid4()
    terms = ContractTerms(
        contract_type=ContractType.FIXED_MONTHLY,
        rate=Money(amount=Decimal("5000.00"), currency="USD"),
        date_range=DateRange(valid_from=date(2024, 1, 1)),
    )
    contract = Contract(employee_id=employee_id, terms=terms, status=ContractStatus.ACTIVE)

    with pytest.raises(ValueError, match="already active"):
        contract.activate()


def test_contract_cancel():
    employee_id = uuid4()
    terms = ContractTerms(
        contract_type=ContractType.FIXED_MONTHLY,
        rate=Money(amount=Decimal("5000.00"), currency="USD"),
        date_range=DateRange(valid_from=date(2024, 1, 1)),
    )
    contract = Contract(employee_id=employee_id, terms=terms, status=ContractStatus.ACTIVE)

    contract.cancel("End of project")
    assert contract.status == ContractStatus.CANCELED
    assert contract.cancellation_reason == "End of project"
    assert contract.canceled_at is not None


def test_contract_expire():
    employee_id = uuid4()
    terms = ContractTerms(
        contract_type=ContractType.FIXED_MONTHLY,
        rate=Money(amount=Decimal("5000.00"), currency="USD"),
        date_range=DateRange(valid_from=date(2024, 1, 1), valid_to=date(2024, 12, 31)),
    )
    contract = Contract(employee_id=employee_id, terms=terms, status=ContractStatus.ACTIVE)

    contract.expire()
    assert contract.status == ContractStatus.EXPIRED


def test_is_active_at():
    employee_id = uuid4()
    terms = ContractTerms(
        contract_type=ContractType.FIXED_MONTHLY,
        rate=Money(amount=Decimal("5000.00"), currency="USD"),
        date_range=DateRange(valid_from=date(2024, 1, 1), valid_to=date(2024, 12, 31)),
    )
    contract = Contract(employee_id=employee_id, terms=terms, status=ContractStatus.ACTIVE)

    assert contract.is_active_at(date(2024, 6, 1)) is True
    assert contract.is_active_at(date(2023, 12, 31)) is False
    assert contract.is_active_at(date(2025, 1, 1)) is False


def test_hourly_contract_requires_hours():
    with pytest.raises(ValueError, match="hours_per_week"):
        ContractTerms(
            contract_type=ContractType.HOURLY,
            rate=Money(amount=Decimal("50.00"), currency="USD"),
            date_range=DateRange(valid_from=date(2024, 1, 1)),
        )


def test_commission_contract_requires_percentage():
    with pytest.raises(ValueError, match="commission_percentage"):
        ContractTerms(
            contract_type=ContractType.COMMISSION_BASED,
            rate=Money(amount=Decimal("1000.00"), currency="USD"),
            date_range=DateRange(valid_from=date(2024, 1, 1)),
        )
