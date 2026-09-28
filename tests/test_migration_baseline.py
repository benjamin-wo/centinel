"""Positive tests for the legacy schema baseline: upgrade, check, comparator."""

import pytest
from sqlalchemy import create_engine, inspect, text
from tests.support.alembic_helpers import (
    run_alembic_upgrade,
    run_alembic_check,
    schema_mismatches,
)
from tests.support.schema_contract import (
    EXPECTED_TABLES,
    KNOWN_EXTRA_TABLES,
)


@pytest.mark.no_sqlite_setup
class TestLegacySchemaBaseline:
    """Verify the Alembic migration produces exactly the source-derived schema."""

    def test_upgrade_creates_all_expected_tables(self, disposable_db_url):
        run_alembic_upgrade(disposable_db_url)
        engine = create_engine(disposable_db_url)
        inspector = inspect(engine)
        actual = set(inspector.get_table_names())
        engine.dispose()

        missing = EXPECTED_TABLES - actual
        assert not missing, f"Tables missing after upgrade: {missing}"
        unexpected = actual - EXPECTED_TABLES - KNOWN_EXTRA_TABLES
        assert not unexpected, f"Unexpected tables found: {unexpected}"

    def test_schema_fully_matches_contract(self, disposable_db_url):
        run_alembic_upgrade(disposable_db_url)
        errors = schema_mismatches(disposable_db_url)
        assert not errors, (
            "Schema contract mismatches:\n  " + "\n  ".join(errors)
        )

    def test_alembic_check_reports_no_drift(self, disposable_db_url):
        """Strict check: any detected drift fails the test."""
        run_alembic_upgrade(disposable_db_url)
        run_alembic_check(disposable_db_url)


@pytest.mark.no_sqlite_setup
class TestCheckpointerExclusion:
    """Verify checkpointer tables are NOT in the Alembic baseline."""

    def test_checkpointer_tables_absent_from_baseline(self, disposable_db_url):
        run_alembic_upgrade(disposable_db_url)
        engine = create_engine(disposable_db_url)
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        engine.dispose()

        checkpointer_tables = {
            "checkpoint_migrations",
            "checkpoints",
            "checkpoint_writes",
            "checkpoint_blobs",
        }
        present = tables & checkpointer_tables
        assert not present, (
            f"Checkpointer tables should not exist: {present}"
        )