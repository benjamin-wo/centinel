"""taskitem and capability request log tables

Creates taskitem (with IOU fields and FKs to userprofile and
expensetransaction) and capabilityrequestlog — the final two tables
completing the legacy schema.

Revision ID: a1b2c3d4e5f2
Revises: a1b2c3d4e5f1
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f2"
down_revision: Union[str, None] = "a1b2c3d4e5f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── taskitem ─────────────────────────────────────────────────────────
    op.create_table(
        "taskitem",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("reminder_type", sa.String(), nullable=False),
        sa.Column("reminder_time", sa.DateTime(), nullable=True),
        sa.Column("cron_expression", sa.String(), nullable=True),
        sa.Column("timezone", sa.String(), nullable=False),
        sa.Column("is_reminder_active", sa.Boolean(), nullable=False),
        sa.Column("linked_expense_id", sa.Integer(), nullable=True),
        sa.Column("iou_friend", sa.String(), nullable=True),
        sa.Column("iou_amount", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_taskitem_user_id", "taskitem", ["user_id"], unique=False,
    )
    op.create_index(
        "ix_taskitem_status", "taskitem", ["status"], unique=False,
    )
    op.create_index(
        "ix_taskitem_priority", "taskitem", ["priority"], unique=False,
    )
    op.create_index(
        "ix_taskitem_linked_expense_id",
        "taskitem", ["linked_expense_id"], unique=False,
    )
    op.create_index(
        "ix_taskitem_iou_friend",
        "taskitem", ["iou_friend"], unique=False,
    )
    op.create_index(
        "ix_taskitem_iou_amount",
        "taskitem", ["iou_amount"], unique=False,
    )
    op.create_foreign_key(
        "fk_taskitem_user_id_userprofile",
        "taskitem", "userprofile",
        ["user_id"], ["user_id"],
    )

    # ── capabilityrequestlog ─────────────────────────────────────────────
    op.create_table(
        "capabilityrequestlog",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("requested_task", sa.String(), nullable=False),
        sa.Column("intent_type", sa.String(), nullable=False),
        sa.Column("missing_capability_tags", sa.String(), nullable=False),
        sa.Column("expectation", sa.String(), nullable=True),
        sa.Column("block_reason", sa.String(), nullable=True),
        sa.Column("agent_reply", sa.String(), nullable=True),
        sa.Column("channel", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_capabilityrequestlog_user_id",
        "capabilityrequestlog", ["user_id"], unique=False,
    )
    op.create_index(
        "ix_capabilityrequestlog_intent_type",
        "capabilityrequestlog", ["intent_type"], unique=False,
    )
    op.create_index(
        "ix_capabilityrequestlog_missing_capability_tags",
        "capabilityrequestlog", ["missing_capability_tags"], unique=False,
    )
    op.create_foreign_key(
        "fk_capabilityrequestlog_user_id_userprofile",
        "capabilityrequestlog", "userprofile",
        ["user_id"], ["user_id"],
    )


def downgrade() -> None:
    raise RuntimeError(
        "Forward-only schema policy: downgrade would drop tables with data. "
        "Create a fresh disposable database and apply alembic upgrade head."
    )