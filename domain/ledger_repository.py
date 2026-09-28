from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import or_, select

from core.models import ExpenseTransaction, IncomeTransaction, UserProfile
from domain.ledger import (
    ExpenseDraft,
    IncomeDraft,
    LedgerEntry,
    LedgerProjection,
    project_ledger,
)


async def save_expense(
    session: AsyncSession,
    user_id: int,
    draft: ExpenseDraft,
    source_message_id: str | None = None,
    is_verified: bool = True,
    source_sender_domain: str | None = None,
    logged_at: datetime | None = None,
    notes: str | None = None,
) -> ExpenseTransaction:
    """Add one user-scoped expense to the current transaction."""
    transaction = ExpenseTransaction(
        user_id=user_id,
        amount=draft.amount,
        currency=draft.currency,
        merchant=draft.merchant,
        category=draft.category,
        date=draft.date,
        source_message_id=source_message_id,
        source_sender_domain=(source_sender_domain or "").lower() or None,
        logged_at=logged_at,
        is_verified=is_verified,
        notes=notes,
    )
    session.add(transaction)
    await session.flush()
    return transaction


async def save_income(
    session: AsyncSession,
    user_id: int,
    draft: IncomeDraft,
    source_message_id: str | None = None,
) -> IncomeTransaction:
    """Add one user-scoped income record to the current transaction."""
    profile = (
        await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    ).scalar_one_or_none()
    if profile is None:
        session.add(
            UserProfile(
                user_id=user_id,
                telegram_chat_id=user_id,
                current_timezone="Asia/Singapore",
            )
        )
        await session.flush()
    transaction = IncomeTransaction(
        user_id=user_id,
        amount=draft.amount,
        currency=draft.currency,
        source=draft.source,
        category=draft.category,
        date=draft.date,
        notes=draft.notes,
        source_message_id=source_message_id,
        linked_expense_id=draft.linked_expense_id,
    )
    session.add(transaction)
    await session.flush()
    return transaction


async def query_unified_ledger(
    session: AsyncSession,
    user_id: int,
    direction: str = "all",
    categories: Optional[Sequence[str]] = None,
    since_date: datetime | None = None,
    until_date: datetime | None = None,
    search_text: str | None = None,
    limit: int = 20,
) -> LedgerProjection:
    """Read both ledger directions through one user-scoped repository contract."""
    outgoing: list[LedgerEntry] = []
    incoming: list[LedgerEntry] = []
    pattern = f"%{search_text}%" if search_text else None
    if direction in {"all", "outgoing"}:
        query = select(ExpenseTransaction).where(ExpenseTransaction.user_id == user_id)
        if categories:
            query = query.where(or_(*[ExpenseTransaction.category == category for category in categories]))
        if since_date:
            query = query.where(ExpenseTransaction.date >= since_date)
        if until_date:
            query = query.where(ExpenseTransaction.date < until_date)
        if pattern:
            query = query.where(or_(ExpenseTransaction.merchant.ilike(pattern), ExpenseTransaction.category.ilike(pattern)))
        rows = (await session.execute(query.order_by(ExpenseTransaction.date.desc()))).scalars().all()
        outgoing = [
            LedgerEntry("outgoing", row.merchant, float(row.amount), row.currency, row.category, row.date)
            for row in rows
        ]
    if direction in {"all", "incoming"}:
        query = select(IncomeTransaction).where(IncomeTransaction.user_id == user_id)
        if categories:
            query = query.where(or_(*[IncomeTransaction.category == category for category in categories]))
        if since_date:
            query = query.where(IncomeTransaction.date >= since_date)
        if until_date:
            query = query.where(IncomeTransaction.date < until_date)
        if pattern:
            query = query.where(or_(IncomeTransaction.source.ilike(pattern), IncomeTransaction.category.ilike(pattern), IncomeTransaction.notes.ilike(pattern)))
        rows = (await session.execute(query.order_by(IncomeTransaction.date.desc()))).scalars().all()
        incoming = [
            LedgerEntry("incoming", row.source, float(row.amount), row.currency, row.category, row.date)
            for row in rows
        ]
    return project_ledger(outgoing + incoming, direction=direction, limit=limit)
