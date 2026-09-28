from datetime import datetime

from domain.ledger import LedgerEntry, project_ledger


def test_project_ledger_merges_directions_and_calculates_currency_nets():
    entries = [
        LedgerEntry("outgoing", "Cafe", 12.50, "SGD", "Dining", datetime(2026, 8, 10)),
        LedgerEntry("incoming", "Acme", 2000.00, "SGD", "Salary", datetime(2026, 8, 1)),
        LedgerEntry("outgoing", "Market", 40.00, "SGD", "Groceries", datetime(2026, 8, 15)),
    ]

    projection = project_ledger(entries, direction="all", limit=20)

    assert projection.money_out["SGD"].total == 52.50
    assert projection.money_out["SGD"].count == 2
    assert projection.money_in["SGD"].total == 2000.00
    assert projection.net["SGD"] == 1947.50
    assert [entry.title for entry in projection.items] == ["Market", "Cafe", "Acme"]


def test_project_ledger_applies_a_positive_limit_without_mutating_entries():
    entries = [
        LedgerEntry("outgoing", "First", 1.00, "SGD", "General", datetime(2026, 8, 1)),
        LedgerEntry("outgoing", "Second", 2.00, "SGD", "General", datetime(2026, 8, 2)),
    ]

    projection = project_ledger(entries, direction="outgoing", limit=0)

    assert len(projection.items) == 1
    assert len(entries) == 2
