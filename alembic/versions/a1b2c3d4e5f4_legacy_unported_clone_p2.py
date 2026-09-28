"""legacy unported clone tables (part 2)

Creates the remaining four application-owned tables from the production
clone that have not yet been refactored into SQLModel table models.

Tables created:
5. productionbuglog     — no FKs, 8 indexes
6. qualityauditlog      — FK → userprofile
7. whiteboardproject    — FK → userprofile, server defaults on cover_ready + section_order
8. whiteboardblock      — FKs → whiteboardproject, expensetransaction, taskitem

Part 2 depends on part 1 (f3), which created busstop, conversationauditlog,
groceryitem, and pointsbalance.

See ``core/legacy_schema.py`` for the full ``sa.Table`` declarations
registered on ``SQLModel.metadata``.

Revision ID: a1b2c3d4e5f4
Revises: a1b2c3d4e5f3
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f4"
down_revision: Union[str, None] = "a1b2c3d4e5f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── productionbuglog ─────────────────────────────────────────────────────
    op.create_table(
        "productionbuglog",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("subsystem", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("fingerprint", sa.String(), nullable=False),
        sa.Column("occurrence_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("detection_source", sa.String(), nullable=False),
        sa.Column("error_traceback", sa.String(), nullable=True),
        sa.Column("github_issue_number", sa.Integer(), nullable=True),
        sa.Column("github_issue_url", sa.String(), nullable=True),
        sa.Column("reproduction_context", sa.String(), nullable=True),
        sa.Column("root_cause", sa.String(), nullable=True),
        sa.Column("suggested_fix", sa.String(), nullable=True),
        sa.Column("thread_id", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_productionbuglog_detection_source",
        "productionbuglog", ["detection_source"], unique=False,
    )
    op.create_index(
        "ix_productionbuglog_fingerprint",
        "productionbuglog", ["fingerprint"], unique=False,
    )
    op.create_index(
        "ix_productionbuglog_severity",
        "productionbuglog", ["severity"], unique=False,
    )
    op.create_index(
        "ix_productionbuglog_status",
        "productionbuglog", ["status"], unique=False,
    )
    op.create_index(
        "ix_productionbuglog_subsystem",
        "productionbuglog", ["subsystem"], unique=False,
    )
    op.create_index(
        "ix_productionbuglog_thread_id",
        "productionbuglog", ["thread_id"], unique=False,
    )
    op.create_index(
        "ix_productionbuglog_title",
        "productionbuglog", ["title"], unique=False,
    )
    op.create_index(
        "ix_productionbuglog_user_id",
        "productionbuglog", ["user_id"], unique=False,
    )

    # ── qualityauditlog ──────────────────────────────────────────────────────
    op.create_table(
        "qualityauditlog",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("thread_id", sa.String(), nullable=False),
        sa.Column("evaluated_at", sa.DateTime(), nullable=False),
        sa.Column("faithfulness_score", sa.Integer(), nullable=False),
        sa.Column("routing_efficiency_score", sa.Integer(), nullable=False),
        sa.Column("hallucination_detected", sa.Boolean(), nullable=False),
        sa.Column("unnecessary_friction_flag", sa.Boolean(), nullable=False),
        sa.Column("evidence_explanation", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_qualityauditlog_hallucination_detected",
        "qualityauditlog", ["hallucination_detected"], unique=False,
    )
    op.create_index(
        "ix_qualityauditlog_thread_id",
        "qualityauditlog", ["thread_id"], unique=False,
    )
    op.create_index(
        "ix_qualityauditlog_user_id",
        "qualityauditlog", ["user_id"], unique=False,
    )
    op.create_foreign_key(
        "fk_qualityauditlog_user_id_userprofile",
        "qualityauditlog", "userprofile",
        ["user_id"], ["user_id"],
    )

    # ── whiteboardproject ────────────────────────────────────────────────────
    op.create_table(
        "whiteboardproject",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("emoji_icon", sa.String(), nullable=False),
        sa.Column("summary", sa.String(), nullable=True),
        sa.Column("cover_ready", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("section_order", sa.JSON(), nullable=True, server_default=sa.text("'[]'::json")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_whiteboardproject_category",
        "whiteboardproject", ["category"], unique=False,
    )
    op.create_index(
        "ix_whiteboardproject_user_id",
        "whiteboardproject", ["user_id"], unique=False,
    )
    op.create_foreign_key(
        "fk_whiteboardproject_user_id_userprofile",
        "whiteboardproject", "userprofile",
        ["user_id"], ["user_id"],
    )

    # ── whiteboardblock ──────────────────────────────────────────────────────
    op.create_table(
        "whiteboardblock",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("section_name", sa.String(), nullable=False),
        sa.Column("block_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content_payload", sa.JSON(), nullable=True),
        sa.Column("position_order", sa.Integer(), nullable=False),
        sa.Column("linked_expense_id", sa.Integer(), nullable=True),
        sa.Column("linked_task_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_whiteboardblock_block_type",
        "whiteboardblock", ["block_type"], unique=False,
    )
    op.create_index(
        "ix_whiteboardblock_project_id",
        "whiteboardblock", ["project_id"], unique=False,
    )
    op.create_index(
        "ix_whiteboardblock_section_name",
        "whiteboardblock", ["section_name"], unique=False,
    )
    op.create_foreign_key(
        "fk_whiteboardblock_project_id_whiteboardproject",
        "whiteboardblock", "whiteboardproject",
        ["project_id"], ["id"],
    )
    op.create_foreign_key(
        "fk_whiteboardblock_linked_expense_id_expensetransaction",
        "whiteboardblock", "expensetransaction",
        ["linked_expense_id"], ["id"],
    )
    op.create_foreign_key(
        "fk_whiteboardblock_linked_task_id_taskitem",
        "whiteboardblock", "taskitem",
        ["linked_task_id"], ["id"],
    )


def downgrade() -> None:
    raise RuntimeError(
        "Forward-only schema policy: downgrade would drop tables with data. "
        "Create a fresh disposable database and apply alembic upgrade head."
    )