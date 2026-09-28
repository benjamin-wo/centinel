"""Legacy schema tables from the production clone not yet ported to SQLModel.

Eight tables exist in the restored 17-table clone that are not (yet) defined
as SQLModel table models.  They are registered here on ``SQLModel.metadata``
so that Alembic manages them, while the application code does not import or
depend on these definitions for its runtime behaviour.

The table contracts below are EXACTLY as observed from the restored clone:
indexes, primary keys, foreign keys, unique constraints, server defaults,
and nullability all match.  No additional application behaviour is attached.
"""

from sqlmodel import SQLModel
import sqlalchemy as sa

# Register all legacy tables on the central SQLModel metadata so that
# Alembic's include_object callback and target_metadata see them.
meta = SQLModel.metadata

# ── busstop ───────────────────────────────────────────────────────────────────

sa.Table(
    "busstop",
    meta,
    sa.Column("code", sa.String(), primary_key=True),
    sa.Column("description", sa.String(), nullable=False),
    sa.Column("road_name", sa.String(), nullable=False),
    sa.Column("lat", sa.Double(), nullable=True),
    sa.Column("lng", sa.Double(), nullable=True),
    sa.Index("ix_busstop_description", "description"),
    sa.Index("ix_busstop_road_name", "road_name"),
)

# ── conversationauditlog ──────────────────────────────────────────────────────

sa.Table(
    "conversationauditlog",
    meta,
    sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
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
    sa.Index("ix_conversationauditlog_thread_id", "thread_id"),
    sa.Index("ix_conversationauditlog_user_id", "user_id"),
    sa.Index("ix_conversationauditlog_verdict", "verdict"),
)

# ── groceryitem ───────────────────────────────────────────────────────────────

sa.Table(
    "groceryitem",
    meta,
    sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("quantity", sa.String(), nullable=False),
    sa.Column("category", sa.String(), nullable=False),
    sa.Column("is_purchased", sa.Boolean(), nullable=False),
    sa.Column("added_at", sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(["user_id"], ["userprofile.user_id"]),
    sa.Index("ix_groceryitem_user_id", "user_id"),
)

# ── pointsbalance ─────────────────────────────────────────────────────────────

sa.Table(
    "pointsbalance",
    meta,
    sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("program", sa.String(), nullable=False),
    sa.Column("issuer", sa.String(), nullable=False),
    sa.Column("balance", sa.Double(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), nullable=False),
    sa.Column("expiry_date", sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(["user_id"], ["userprofile.user_id"]),
    sa.UniqueConstraint("user_id", "issuer", "program", name="uq_points_user_issuer_program"),
    sa.Index("ix_pointsbalance_user_id", "user_id"),
    sa.Index("ix_pointsbalance_issuer", "issuer"),
    sa.Index("ix_pointsbalance_program", "program"),
)

# ── productionbuglog ──────────────────────────────────────────────────────────

sa.Table(
    "productionbuglog",
    meta,
    sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
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
    sa.Index("ix_productionbuglog_detection_source", "detection_source"),
    sa.Index("ix_productionbuglog_fingerprint", "fingerprint"),
    sa.Index("ix_productionbuglog_severity", "severity"),
    sa.Index("ix_productionbuglog_status", "status"),
    sa.Index("ix_productionbuglog_subsystem", "subsystem"),
    sa.Index("ix_productionbuglog_thread_id", "thread_id"),
    sa.Index("ix_productionbuglog_title", "title"),
    sa.Index("ix_productionbuglog_user_id", "user_id"),
)

# ── qualityauditlog ───────────────────────────────────────────────────────────

sa.Table(
    "qualityauditlog",
    meta,
    sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("thread_id", sa.String(), nullable=False),
    sa.Column("evaluated_at", sa.DateTime(), nullable=False),
    sa.Column("faithfulness_score", sa.Integer(), nullable=False),
    sa.Column("routing_efficiency_score", sa.Integer(), nullable=False),
    sa.Column("hallucination_detected", sa.Boolean(), nullable=False),
    sa.Column("unnecessary_friction_flag", sa.Boolean(), nullable=False),
    sa.Column("evidence_explanation", sa.String(), nullable=False),
    sa.ForeignKeyConstraint(["user_id"], ["userprofile.user_id"]),
    sa.Index("ix_qualityauditlog_hallucination_detected", "hallucination_detected"),
    sa.Index("ix_qualityauditlog_thread_id", "thread_id"),
    sa.Index("ix_qualityauditlog_user_id", "user_id"),
)

# ── whiteboardproject ─────────────────────────────────────────────────────────

sa.Table(
    "whiteboardproject",
    meta,
    sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("title", sa.String(), nullable=False),
    sa.Column("category", sa.String(), nullable=False),
    sa.Column("emoji_icon", sa.String(), nullable=False),
    sa.Column("summary", sa.String(), nullable=True),
    sa.Column("cover_ready", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    sa.Column("section_order", sa.JSON(), nullable=True, server_default=sa.text("'[]'::json")),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(["user_id"], ["userprofile.user_id"]),
    sa.Index("ix_whiteboardproject_category", "category"),
    sa.Index("ix_whiteboardproject_user_id", "user_id"),
)

# ── whiteboardblock ───────────────────────────────────────────────────────────

sa.Table(
    "whiteboardblock",
    meta,
    sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
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
    sa.ForeignKeyConstraint(["project_id"], ["whiteboardproject.id"]),
    sa.ForeignKeyConstraint(["linked_expense_id"], ["expensetransaction.id"]),
    sa.ForeignKeyConstraint(["linked_task_id"], ["taskitem.id"]),
    sa.Index("ix_whiteboardblock_block_type", "block_type"),
    sa.Index("ix_whiteboardblock_project_id", "project_id"),
    sa.Index("ix_whiteboardblock_section_name", "section_name"),
)