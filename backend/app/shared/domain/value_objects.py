from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

SUPPORTED_CURRENCIES = {
    "USD",
    "EUR",
    "GBP",
    "JPY",
    "CHF",
    "CAD",
    "AUD",
    "NZD",
    "SEK",
    "NOK",
    "DKK",
    "PLN",
    "CZK",
    "HUF",
    "RON",
    "BGN",
    "HRK",
    "RSD",
    "UAH",
    "RUB",
    "TRY",
    "ILS",
    "ZAR",
    "INR",
    "CNY",
    "KRW",
    "THB",
    "MYR",
    "SGD",
    "IDR",
    "PHP",
    "VND",
    "BRL",
    "MXN",
    "ARS",
    "CLP",
    "COP",
    "PEN",
}


@dataclass(frozen=True)
class DateRange:
    valid_from: date
    valid_to: Optional[date] = None

    def __post_init__(self):
        if self.valid_to and self.valid_from > self.valid_to:
            raise ValueError("valid_from must be before valid_to")

    @property
    def start_date(self) -> date:
        return self.valid_from

    @property
    def end_date(self) -> Optional[date]:
        return self.valid_to

    def contains(self, check_date: date) -> bool:
        return self.is_active_at(check_date)

    def is_active_at(self, check_date: date) -> bool:
        if check_date < self.valid_from:
            return False
        if self.valid_to and check_date > self.valid_to:
            return False
        return True

    def overlaps_with(self, other: "DateRange") -> bool:
        if self.valid_to and other.valid_from > self.valid_to:
            return False
        if other.valid_to and self.valid_from > other.valid_to:
            return False
        return True


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if self.currency not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {self.currency}")

        object.__setattr__(self, "amount", Decimal(str(self.amount)))

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} to {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {other.currency} from {self.currency}")
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Result cannot be negative")
        return Money(result_amount, self.currency)

    def __mul__(self, multiplier: Decimal | int | float) -> "Money":
        if not isinstance(multiplier, (Decimal, int, float)):
            raise TypeError("Can only multiply Money by a number")
        return Money(self.amount * Decimal(str(multiplier)), self.currency)

    def __rmul__(self, multiplier: Decimal | int | float) -> "Money":
        return self.__mul__(multiplier)

    def __truediv__(self, divisor: Decimal | int | float) -> "Money":
        if not isinstance(divisor, (Decimal, int, float)):
            raise TypeError("Can only divide Money by a number")
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / Decimal(str(divisor)), self.currency)

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money to Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} to {other.currency}")
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money to Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} to {other.currency}")
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money to Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} to {other.currency}")
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money to Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} to {other.currency}")
        return self.amount >= other.amount

    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency='{self.currency}')"

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
