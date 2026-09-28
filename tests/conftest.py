import asyncio
import pytest
import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy import Table
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
import core.db as db_mod
import core.models  # noqa: F401 - ensure models are registered with SQLModel.metadata

TEST_DB_PATH = "./test_testdb.sqlite"

# Snapshot the 9 application-model table objects at import time, before any
# Alembic operation imports core.legacy_schema (which registers 8 PostgreSQL-
# specific legacy tables on the same global SQLModel.metadata).  The autouse
# SQLite fixture uses this snapshot so it never tries to CREATE/DROP the
# legacy tables, whose '[]'::json and similar PostgreSQL-only defaults would
# crash on SQLite.
_APP_TABLES: list[Table] = list(SQLModel.metadata.tables.values())

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "no_sqlite_setup: skip the autouse SQLite metadata setup/teardown "
        "fixture (used by schema-contract tests that manage their own "
        "PostgreSQL disposable database).",
    )

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db(request):
    """Initialize database schema before each test and drop after.

    Skip if the test or its class is marked ``no_sqlite_setup`` — used by
    schema-contract tests that manage their own PostgreSQL disposable database
    and whose legacy tables contain PostgreSQL-specific server_default
    expressions that SQLite cannot execute.

    Only the 9 original application-model tables are created/dropped (via
    the ``_APP_TABLES`` snapshot).  Clone-derived legacy tables registered
    later on ``SQLModel.metadata`` by Alembic operations are intentionally
    excluded — they use PostgreSQL-only DDL.
    """
    if request.node.get_closest_marker("no_sqlite_setup"):
        yield
        return
    async with db_mod.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all, tables=_APP_TABLES)
    yield
    async with db_mod.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all, tables=_APP_TABLES)


# ── PostgreSQL disposable-database fixture for schema tests ──────────────────

from tests.support.alembic_helpers import (
    create_disposable_db,
    drop_disposable_db,
    local_postgres_url,
)


@pytest.fixture(scope="module")
def disposable_db_url():
    """Create + tear down one unique disposable database per module."""
    db_name = create_disposable_db()
    try:
        yield local_postgres_url(db_name)
    finally:
        drop_disposable_db(db_name)


@pytest.fixture
def unique_db():
    """Yield a disposable URL per test; teardown even on failure."""
    db_name = create_disposable_db()
    url = local_postgres_url(db_name)
    try:
        yield url
    finally:
        drop_disposable_db(db_name)
