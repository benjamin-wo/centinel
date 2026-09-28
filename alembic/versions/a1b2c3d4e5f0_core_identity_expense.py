"""core identity and expense tables

Creates userprofile, usercredential, and expensetransaction — the three
central tables that most others reference via foreign key.

Revision ID: a1b2c3d4e5f0
Revises: None
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── userprofile ──────────────────────────────────────────────────────
    op.create_table(
        "userprofile",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("telegram_chat_id", sa.Integer(), nullable=False),
        sa.Column("current_timezone", sa.String(), nullable=False),
        sa.Column("home_currency", sa.String(), nullable=False),
        sa.Column("tracked_banks", sa.JSON(), nullable=True),
        sa.Column("email_exclude_domains", sa.JSON(), nullable=True,
                  server_default=sa.text("'[]'::json")),
        sa.Column("email_content_type_presets", sa.JSON(), nullable=True,
                  server_default=sa.text("'[]'::json")),
        sa.Column("whiteboard_seeded", sa.Boolean(), nullable=False,
                  server_default=sa.text("false")),
        sa.Column("last_whiteboard_id", sa.Integer(), nullable=True),
        sa.Column("last_email_digest_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(
        "ix_userprofile_telegram_chat_id",
        "userprofile", ["telegram_chat_id"], unique=True,
    )

    # ── usercredential ───────────────────────────────────────────────────
    op.create_table(
        "usercredential",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("encrypted_token_payload", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_usercredential_user_id", "usercredential", ["user_id"], unique=False,
    )
    op.create_index(
        "ix_usercredential_provider", "usercredential", ["provider"], unique=False,
    )
    op.create_foreign_key(
        "fk_usercredential_user_id_userprofile",
        "usercredential", "userprofile",
        ["user_id"], ["user_id"],
    )

    # ── expensetransaction ───────────────────────────────────────────────
    op.create_table(
        "expensetransaction",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("merchant", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("source_message_id", sa.String(), nullable=True),
        sa.Column("source_sender_domain", sa.String(), nullable=True),
        sa.Column("logged_at", sa.DateTime(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("receipt_items", sa.JSON(), nullable=True,
                  server_default=sa.text("'[]'::json")),
        sa.Column("split_data", sa.JSON(), nullable=True,
                  server_default=sa.text("'{}'::json")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_expensetransaction_user_id",
        "expensetransaction", ["user_id"], unique=False,
    )
    op.create_index(
        "ix_expensetransaction_source_message_id",
        "expensetransaction", ["source_message_id"], unique=True,
    )
    op.create_foreign_key(
        "fk_expensetransaction_user_id_userprofile",
        "expensetransaction", "userprofile",
        ["user_id"], ["user_id"],
    )


def downgrade() -> None:
    raise RuntimeError(
        "Forward-only schema policy: downgrade from the legacy baseline "
        "would drop tables with data.  Create a fresh disposable database "
        "and apply alembic upgrade head instead."
    )