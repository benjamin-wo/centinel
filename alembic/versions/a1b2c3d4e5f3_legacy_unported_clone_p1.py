"""legacy unported clone tables (part 1)

Creates the first four application-owned tables from the production clone
that have not yet been refactored into SQLModel table models.

Tables created:
1. busstop              — no FKs
2. conversationauditlog — no FKs
3. groceryitem          — FK → userprofile
4. pointsbalance        — FK → userprofile, unique constraint

See ``core/legacy_schema.py`` for the full ``sa.Table`` declarations
registered on ``SQLModel.metadata``.

Revision ID: a1b2c3d4e5f3
Revises: a1b2c3d4e5f2
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f3"
down_revision: Union[str, None] = "a1b2c3d4e5f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── busstop ──────────────────────────────────────────────────────────────
    op.create_table(
        "busstop",
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("road_name", sa.String(), nullable=False),
        sa.Column("lat", sa.Double(), nullable=True),
        sa.Column("lng", sa.Double(), nullable=True),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_index(
        "ix_busstop_description", "busstop", ["description"], unique=False,
    )
    op.create_index(
        "ix_busstop_road_name", "busstop", ["road_name"], unique=False,
    )

    # ── conversationauditlog ─────────────────────────────────────────────────
    op.create_table(
        "conversationauditlog",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("thread_id", sa.String(), nullable=False),
        sa.Column("message_count", sa.Integer(), nullable=False),
        sa.Column("judge_model", sa.String(), nullable=False),
        sa.Column("faithfulness_score", sa.Integer(), nullable=False),
        sa.Column("helpfulness_score", sa.Integer(), nullable=False),
        sa.Column("routing_score", sa.Integer(), nullable=False),
        sa.Column("tool_correctness_score", sa.Integer(), nullable=False),
        sa.Column("verdict", sa.String(), nullable=False),
        sa.Column("evidence", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_conversationauditlog_thread_id",
        "conversationauditlog", ["thread_id"], unique=False,
    )
    op.create_index(
        "ix_conversationauditlog_user_id",
        "conversationauditlog", ["user_id"], unique=False,
    )
    op.create_index(
        "ix_conversationauditlog_verdict",
        "conversationauditlog", ["verdict"], unique=False,
    )

    # ── groceryitem ──────────────────────────────────────────────────────────
    op.create_table(
        "groceryitem",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("quantity", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("is_purchased", sa.Boolean(), nullable=False),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_groceryitem_user_id", "groceryitem", ["user_id"], unique=False,
    )
    op.create_foreign_key(
        "fk_groceryitem_user_id_userprofile",
        "groceryitem", "userprofile",
        ["user_id"], ["user_id"],
    )

    # ── pointsbalance ────────────────────────────────────────────────────────
    op.create_table(
        "pointsbalance",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("program", sa.String(), nullable=False),
        sa.Column("issuer", sa.String(), nullable=False),
        sa.Column("balance", sa.Double(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("expiry_date", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_pointsbalance_user_id", "pointsbalance", ["user_id"], unique=False,
    )
    op.create_index(
        "ix_pointsbalance_issuer", "pointsbalance", ["issuer"], unique=False,
    )
    op.create_index(
        "ix_pointsbalance_program", "pointsbalance", ["program"], unique=False,
    )
    op.create_unique_constraint(
        "uq_points_user_issuer_program",
        "pointsbalance", ["user_id", "issuer", "program"],
    )
    op.create_foreign_key(
        "fk_pointsbalance_user_id_userprofile",
        "pointsbalance", "userprofile",
        ["user_id"], ["user_id"],
    )


def downgrade() -> None:
    raise RuntimeError(
        "Forward-only schema policy: downgrade would drop tables with data. "
        "Create a fresh disposable database and apply alembic upgrade head."
    )