from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Mapping, Sequence


LedgerDirection = Literal["incoming", "outgoing"]


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    direction: LedgerDirection
    title: str
    amount: float
    currency: str
    category: str
    date: datetime


@dataclass(frozen=True, slots=True)
class ExpenseDraft:
    amount: float
    currency: str
    merchant: str
    category: str
    date: datetime


@dataclass(frozen=True, slots=True)
class IncomeDraft:
    amount: float
    currency: str
    source: str
    category: str
    date: datetime
    notes: str | None = None
    linked_expense_id: int | None = None


@dataclass(frozen=True, slots=True)
class CurrencyTotal:
    total: float
    count: int


@dataclass(frozen=True, slots=True)
class LedgerProjection:
    direction: str
    money_out: Mapping[str, CurrencyTotal]
    money_in: Mapping[str, CurrencyTotal]
    net: Mapping[str, float]
    items: tuple[LedgerEntry, ...]
    total_matched: int


def project_ledger(
    entries: Sequence[LedgerEntry],
    direction: str = "all",
    limit: int = 20,
) -> LedgerProjection:
    """Build the shared, read-only ledger projection from normalized entries."""
    wanted = {"incoming", "outgoing"} if direction == "all" else {direction}
    selected = [entry for entry in entries if entry.direction in wanted]
    ordered = tuple(sorted(selected, key=lambda entry: entry.date, reverse=True))
    outgoing = _totals(entry for entry in selected if entry.direction == "outgoing")
    incoming = _totals(entry for entry in selected if entry.direction == "incoming")
    currencies = sorted(set(outgoing) | set(incoming))
    net = {
        currency: round(
            incoming.get(currency, CurrencyTotal(0.0, 0)).total
            - outgoing.get(currency, CurrencyTotal(0.0, 0)).total,
            2,
        )
        for currency in currencies
    }
    return LedgerProjection(
        direction=direction,
        money_out=outgoing,
        money_in=incoming,
        net=net,
        items=ordered[: max(1, limit)],
        total_matched=len(ordered),
    )


def _totals(entries: Sequence[LedgerEntry]) -> dict[str, CurrencyTotal]:
    totals: dict[str, CurrencyTotal] = {}
    for entry in entries:
        current = totals.get(entry.currency, CurrencyTotal(0.0, 0))
        totals[entry.currency] = CurrencyTotal(
            total=current.total + entry.amount,
            count=current.count + 1,
        )
    return totals
