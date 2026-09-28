"""income, undo, tombstone, and scheduled job tables

Creates incometransaction, deletedexpensemessage, expenseundoentry, and
scheduledjob — referenced by taskitem but not yet having forward FKs.

Revision ID: a1b2c3d4e5f1
Revises: a1b2c3d4e5f0
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f1"
down_revision: Union[str, None] = "a1b2c3d4e5f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── incometransaction ────────────────────────────────────────────────
    op.create_table(
        "incometransaction",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("source_message_id", sa.String(), nullable=True),
        sa.Column("linked_expense_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_incometransaction_user_id",
        "incometransaction", ["user_id"], unique=False,
    )
    op.create_index(
        "ix_incometransaction_source",
        "incometransaction", ["source"], unique=False,
    )
    op.create_index(
        "ix_incometransaction_category",
        "incometransaction", ["category"], unique=False,
    )
    op.create_index(
        "ix_incometransaction_source_message_id",
        "incometransaction", ["source_message_id"], unique=True,
    )
    op.create_index(
        "ix_incometransaction_linked_expense_id",
        "incometransaction", ["linked_expense_id"], unique=False,
    )
    op.create_foreign_key(
        "fk_incometransaction_user_id_userprofile",
        "incometransaction", "userprofile",
        ["user_id"], ["user_id"],
    )

    # ── deletedexpensemessage ────────────────────────────────────────────
    op.create_table(
        "deletedexpensemessage",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("source_message_id", sa.String(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_deletedexpensemessage_user_id",
        "deletedexpensemessage", ["user_id"], unique=False,
    )
    op.create_index(
        "ix_deletedexpensemessage_source_message_id",
        "deletedexpensemessage", ["source_message_id"], unique=True,
    )

    # ── expenseundoentry ─────────────────────────────────────────────────
    op.create_table(
        "expenseundoentry",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expense_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_expenseundoentry_user_id",
        "expenseundoentry", ["user_id"], unique=False,
    )
    op.create_index(
        "ix_expenseundoentry_expense_id",
        "expenseundoentry", ["expense_id"], unique=False,
    )
    op.create_index(
        "ix_expenseundoentry_kind",
        "expenseundoentry", ["kind"], unique=False,
    )

    # ── scheduledjob ─────────────────────────────────────────────────────
    op.create_table(
        "scheduledjob",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_name", sa.String(), nullable=False),
        sa.Column("cron_expression", sa.String(), nullable=False),
        sa.Column("instruction_prompt", sa.String(), nullable=False),
        sa.Column("timezone", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_scheduledjob_user_id",
        "scheduledjob", ["user_id"], unique=False,
    )
    op.create_foreign_key(
        "fk_scheduledjob_user_id_userprofile",
        "scheduledjob", "userprofile",
        ["user_id"], ["user_id"],
    )


def downgrade() -> None:
    raise RuntimeError(
        "Forward-only schema policy: downgrade would drop tables with data. "
        "Create a fresh disposable database and apply alembic upgrade head."
    )