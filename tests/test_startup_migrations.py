import re

import pytest
from sqlalchemy import event, text

import core.db as db_mod


ALEMBIC_HEAD = "a1b2c3d4e5f4"


async def _drop_alembic_version() -> None:
    async with db_mod.engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))


@pytest.fixture(autouse=True)
async def clean_migration_marker():
    await _drop_alembic_version()
    yield
    await _drop_alembic_version()


@pytest.mark.asyncio
async def test_unmigrated_database_fails_closed():
    with pytest.raises(RuntimeError, match="alembic upgrade head"):
        await db_mod.verify_migration()


@pytest.mark.asyncio
async def test_reviewed_alembic_head_is_accepted():
    async with db_mod.engine.begin() as conn:
        await conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        await conn.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:version)"),
            {"version": ALEMBIC_HEAD},
        )

    await db_mod.verify_migration()


@pytest.mark.asyncio
async def test_migration_verification_emits_no_ddl():
    async with db_mod.engine.begin() as conn:
        await conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        await conn.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:version)"),
            {"version": ALEMBIC_HEAD},
        )

    statements: list[str] = []

    def capture_sql(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(db_mod.engine.sync_engine, "before_cursor_execute", capture_sql)
    try:
        await db_mod.verify_migration()
    finally:
        event.remove(db_mod.engine.sync_engine, "before_cursor_execute", capture_sql)

    assert statements
    assert not any(re.match(r"\s*(CREATE|ALTER|DROP)\b", sql, re.IGNORECASE) for sql in statements)
