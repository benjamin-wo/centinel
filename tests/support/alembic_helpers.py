"""Database and Alembic helpers for baseline migration tests.

Shared by test_migration_baseline.py and test_schema_safety.py.
"""

import re
import uuid
from pathlib import Path
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect, text

from tests.support.schema_contract import (
    EXPECTED_TABLES,
    EXPECTED_COLUMNS,
    EXPECTED_INDEXES,
    EXPECTED_PKS,
    EXPECTED_FKS,
    EXPECTED_SERVER_DEFAULTS,
    EXPECTED_SEQUENCE_COLUMNS,
    KNOWN_EXTRA_TABLES,
    normalize_type,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ALEMBIC_CFG_PATH = PROJECT_ROOT / "alembic.ini"


def local_postgres_url(db_name: str) -> str:
    return f"postgresql:///{db_name}?host=/tmp"


def create_disposable_db() -> str:
    db_name = f"np_baseline_test_{uuid.uuid4().hex[:12]}"
    maint_engine = create_engine(
        "postgresql:///postgres?host=/tmp",
        isolation_level="AUTOCOMMIT",
    )
    with maint_engine.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    maint_engine.dispose()
    return db_name


def drop_disposable_db(db_name: str) -> None:
    if not db_name.startswith("np_baseline_test_"):
        return
    maint_engine = create_engine(
        "postgresql:///postgres?host=/tmp",
        isolation_level="AUTOCOMMIT",
    )
    with maint_engine.connect() as conn:
        conn.execute(
            text(
                "SELECT pg_terminate_backend(pg_stat_activity.pid) "
                "FROM pg_stat_activity "
                "WHERE pg_stat_activity.datname = :dbname "
                "AND pid <> pg_backend_pid()"
            ),
            {"dbname": db_name},
        )
        conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))
    maint_engine.dispose()


def run_alembic_upgrade(sync_db_url: str) -> None:
    cfg = Config(str(ALEMBIC_CFG_PATH))
    cfg.set_main_option("sqlalchemy.url", sync_db_url)
    command.upgrade(cfg, "head")


def run_alembic_check(sync_db_url: str) -> None:
    cfg = Config(str(ALEMBIC_CFG_PATH))
    cfg.set_main_option("sqlalchemy.url", sync_db_url)
    command.check(cfg)


def run_alembic_downgrade(sync_db_url: str) -> None:
    cfg = Config(str(ALEMBIC_CFG_PATH))
    cfg.set_main_option("sqlalchemy.url", sync_db_url)
    command.downgrade(cfg, "-1")


def schema_mismatches(url: str) -> list[str]:
    """Return list of schema mismatches; empty means exact match."""
    errors: list[str] = []
    engine = create_engine(url)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    for tn in EXPECTED_TABLES:
        if tn not in tables:
            errors.append(f"table '{tn}' is missing")

    unexpected_tables = tables - EXPECTED_TABLES - KNOWN_EXTRA_TABLES
    for tn in sorted(unexpected_tables):
        errors.append(f"unexpected table '{tn}' exists")

    for tn in sorted(EXPECTED_TABLES & tables):
        _check_columns(inspector, tn, errors)
        _check_indexes(inspector, tn, errors)
        _check_pk(inspector, tn, errors)
        _check_fks(inspector, tn, errors)
        _check_server_defaults(inspector, tn, errors)

    engine.dispose()
    return errors


def _check_columns(inspector, tn: str, errors: list[str]) -> None:
    actual_by_name = {
        c["name"]: (normalize_type(str(c["type"])), c["nullable"])
        for c in inspector.get_columns(tn)
    }
    expected_col_names = {c[0] for c in EXPECTED_COLUMNS.get(tn, [])}
    actual_col_names = set(actual_by_name)

    for col_name, col_type, col_nullable in EXPECTED_COLUMNS.get(tn, []):
        canon_expected = normalize_type(col_type)
        if col_name not in actual_by_name:
            errors.append(f"{tn}.{col_name}: column not found")
        else:
            act_type, act_nullable = actual_by_name[col_name]
            if canon_expected != act_type:
                errors.append(
                    f"{tn}.{col_name}: expected type '{col_type}' "
                    f"(canonical '{canon_expected}'), "
                    f"got '{act_type}'"
                )
            if col_nullable != act_nullable:
                errors.append(
                    f"{tn}.{col_name}: expected nullable="
                    f"{col_nullable}, got {act_nullable}"
                )

    unexpected_cols = actual_col_names - expected_col_names
    for c in sorted(unexpected_cols):
        errors.append(f"{tn}: unexpected column '{c}'")


def _check_indexes(inspector, tn: str, errors: list[str]) -> None:
    actual_indexes = {
        (i["name"], tuple(i["column_names"]), i["unique"])
        for i in inspector.get_indexes(tn)
    }
    expected_index_set = {
        (name, tuple(cols), uniq)
        for name, cols, uniq in EXPECTED_INDEXES.get(tn, [])
    }
    for idx_name, idx_cols, idx_unique in EXPECTED_INDEXES.get(tn, []):
        key = (idx_name, tuple(idx_cols), idx_unique)
        if key not in actual_indexes:
            errors.append(
                f"{tn} index '{idx_name}' on {idx_cols} "
                f"(unique={idx_unique}) not found"
            )

    unexpected_idx = actual_indexes - expected_index_set
    for idx_name, idx_cols, idx_uniq in sorted(unexpected_idx):
        errors.append(
            f"{tn}: unexpected index '{idx_name}' "
            f"on {list(idx_cols)} (unique={idx_uniq})"
        )


def _check_pk(inspector, tn: str, errors: list[str]) -> None:
    pk_info = inspector.get_pk_constraint(tn)
    actual_pk_cols = sorted(pk_info.get("constrained_columns", []))
    expected_pk_cols = sorted(EXPECTED_PKS.get(tn, []))
    if actual_pk_cols != expected_pk_cols:
        errors.append(
            f"{tn}: expected PK {expected_pk_cols}, got {actual_pk_cols}"
        )


def _check_fks(inspector, tn: str, errors: list[str]) -> None:
    actual_fks_raw = inspector.get_foreign_keys(tn)
    actual_fk_set: set[tuple[str, str, str]] = set()
    for fk in actual_fks_raw:
        constrained = tuple(fk.get("constrained_columns", []))
        referred_table = fk.get("referred_table", "")
        referred_cols = tuple(fk.get("referred_columns", []))
        if constrained and referred_table:
            actual_fk_set.add((constrained, referred_table, referred_cols))

    expected_fks = EXPECTED_FKS.get(tn, [])
    for constrained, ref_table, ref_cols in expected_fks:
        key = (tuple(constrained), ref_table, tuple(ref_cols))
        if key not in actual_fk_set:
            errors.append(
                f"{tn}: missing FK {constrained} -> {ref_table}.{ref_cols}"
            )

    unexpected_fk = actual_fk_set - {
        (tuple(c), r, tuple(rc)) for c, r, rc in expected_fks
    }
    for constrained, ref_table, ref_cols in sorted(unexpected_fk):
        errors.append(
            f"{tn}: unexpected FK {list(constrained)} -> "
            f"{ref_table}.{list(ref_cols)}"
        )


_SEQUENCE_DEFAULT_RE = re.compile(r"^nextval\([^)]+::regclass\)$")


def _check_server_defaults(inspector, tn: str, errors: list[str]) -> None:
    """Compare literal and sequence server defaults against the contract.

    For each column:
    - If the column is in EXPECTED_SEQUENCE_COLUMNS, assert it has a
      ``nextval(...)`` default.
    - If the column is in EXPECTED_SERVER_DEFAULTS, assert exact match.
    - If neither, assert no non-None, non-sequence default exists.
    - Any ``nextval(...)`` default on a non-expected column is flagged.
    """
    for col in inspector.get_columns(tn):
        col_name = col["name"]
        default: str | None = col.get("default")
        key = f"{tn}.{col_name}"
        is_seq = bool(default and _SEQUENCE_DEFAULT_RE.match(default))

        if key in EXPECTED_SEQUENCE_COLUMNS:
            if not is_seq:
                errors.append(
                    f"{key}: missing expected sequence default, "
                    f"got {default!r}"
                )
        elif is_seq:
            errors.append(
                f"{key}: unexpected sequence default '{default}'"
            )
        else:
            expected = EXPECTED_SERVER_DEFAULTS.get(key)
            if expected is None and default is not None:
                errors.append(f"{key}: unexpected default '{default}'")
            elif expected is not None and default is None:
                errors.append(
                    f"{key}: missing expected default '{expected}'"
                )
            elif expected is not None and default != expected:
                errors.append(
                    f"{key}: expected default '{expected}', "
                    f"got '{default}'"
                )