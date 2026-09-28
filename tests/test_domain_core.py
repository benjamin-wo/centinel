from datetime import datetime

import pytest

from core.db import async_session_factory
from domain.ledger import ExpenseDraft, IncomeDraft
from domain.ledger_repository import query_unified_ledger, save_expense, save_income


@pytest.mark.asyncio
async def test_ledger_repository_round_trip_and_user_scope():
    user_id = 7401
    other_user_id = 7402
    async with async_session_factory() as session:
        await save_expense(
            session,
            user_id,
            ExpenseDraft(12.50, "SGD", "Cafe", "Dining", datetime(2026, 8, 10)),
            source_message_id="domain-expense-7401",
        )
        await save_income(
            session,
            user_id,
            IncomeDraft(100.00, "SGD", "Employer", "Salary", datetime(2026, 8, 1)),
            source_message_id="domain-income-7401",
        )
        await save_expense(
            session,
            other_user_id,
            ExpenseDraft(999.00, "SGD", "Private", "Shopping", datetime(2026, 8, 9)),
            source_message_id="domain-expense-7402",
        )
        await session.commit()

        projection = await query_unified_ledger(session, user_id)

    assert projection.total_matched == 2
    assert projection.money_out["SGD"].total == pytest.approx(12.50)
    assert projection.money_in["SGD"].total == pytest.approx(100.00)
    assert projection.net["SGD"] == pytest.approx(87.50)
    assert {entry.title for entry in projection.items} == {"Cafe", "Employer"}
