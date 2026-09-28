"""Alembic environment configuration for nexus-prime.

Uses a synchronous SQLAlchemy engine (psycopg2) so that migration scripts
run with the standard ``connection.execute()`` API.  The target database URL
is read from the Alembic config (set programmatically by the test harness
or from the ``DATABASE_URL`` environment variable in production).

Checkpointer tables owned by the LangGraph checkpoint package are excluded
from Alembic management — see the ``include_object`` callback.

URL SAFETY
``_reject_unsafe_url()`` is called before any connection is opened.  It
refuses to migrate against any host that is not a local Unix socket,
localhost, or 127.0.0.1.  This prevents accidental production migration.
The error message intentionally omits the URL, user, and password to avoid
credential leakage in logs.
"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure all SQLModel tables are registered with metadata before we capture it.
import core.models  # noqa: F401
import core.legacy_schema  # noqa: F401 — register the 8 clone-derived legacy tables
from core._schema_safety import reject_unsafe_url
from sqlmodel import SQLModel

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


# ── Exclude checkpointer tables from Alembic management ──────────────────────
CHECKPOINTER_TABLES = {
    "checkpoint_migrations",
    "checkpoints",
    "checkpoint_writes",
    "checkpoint_blobs",
    "message_store",
    "checkpoint_versions",
}


# ── URL safety guard ─────────────────────────────────────────────────────────
# reject_unsafe_url() lives in core/_schema_safety.py so that both env.py
# and tests/test_migration_baseline.py share the same implementation.


def include_object(obj, name, type_, reflected, compare_to):
    """Return True for objects Alembic should manage, False to exclude."""
    if type_ == "table" and name in CHECKPOINTER_TABLES:
        return False
    return True


# ── Migration runners ────────────────────────────────────────────────────────


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL without a connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    # Prefer the URL from config (set programmatically or via DATABASE_URL).
    url = config.get_main_option("sqlalchemy.url")
    if url == "placeholder":
        url = os.environ.get("DATABASE_URL", "placeholder")

    # Safety gate: refuse to migrate remote/production hosts.
    if url != "placeholder":
        reject_unsafe_url(url)

    cfg_section = config.get_section(config.config_ini_section, {})
    cfg_section["sqlalchemy.url"] = url

    connectable = engine_from_config(
        cfg_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()