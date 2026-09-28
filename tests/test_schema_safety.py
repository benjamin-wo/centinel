"""Negative tests: URL guard and downgrade safety."""

import pytest
from sqlalchemy import create_engine, inspect
from core._schema_safety import reject_unsafe_url
from tests.support.alembic_helpers import (
    run_alembic_upgrade,
    run_alembic_downgrade,
)
from tests.support.schema_contract import EXPECTED_TABLES


# ── URL guard tests (exercises real reject_unsafe_url from core) ─────────────


@pytest.mark.no_sqlite_setup
class TestURLGuardNegative:
    """Prove the URL guard rejects unsafe targets without leaking secrets."""

    def test_remote_host_rejected(self):
        bad = [
            "postgresql://user:pass@host:5432/np_baseline_test_abc",
            "postgresql://user@railway.app:5432/np_baseline_test_def",
            "postgresql://user:pass@xxx.rds.amazonaws.com:5432/np_baseline_test_a",
        ]
        for url in bad:
            with pytest.raises(RuntimeError, match="Refusing to migrate a non-local"):
                reject_unsafe_url(url)

    def test_local_production_name_rejected(self):
        bad = [
            "postgresql:///production?host=/tmp",
            "postgresql://localhost:5432/proddb",
            "postgresql://127.0.0.1:5432/nexus-prime",
            "postgresql:///postgres?host=/tmp",
        ]
        for url in bad:
            with pytest.raises(RuntimeError):
                reject_unsafe_url(url)

    def test_local_unmarked_db_rejected(self):
        bad = [
            "postgresql:///some_random_db?host=/tmp",
            "postgresql://localhost:5432/myapp_dev",
            "postgresql://127.0.0.1:5432/test",
        ]
        for url in bad:
            with pytest.raises(RuntimeError):
                reject_unsafe_url(url)

    def test_disposable_url_accepted(self):
        safe = [
            "postgresql:///np_baseline_test_a1b2c3d4e5f6?host=/tmp",
            "postgresql://localhost:5432/np_baseline_test_a1b2c3d4e5f6",
        ]
        for url in safe:
            reject_unsafe_url(url)

    def test_error_message_leaks_nothing(self):
        cases = [
            ("postgresql://secretuser:secretpass@railway.app:5432/np_baseline_test_abc",
             ["secretuser", "secretpass", "railway.app"]),
            ("postgresql:///production?host=/tmp", ["production", "/tmp"]),
            ("postgresql:///some_unnamed_db?host=/tmp", ["some_unnamed_db", "/tmp"]),
        ]
        for bad_url, forbidden in cases:
            with pytest.raises(RuntimeError) as exc_info:
                reject_unsafe_url(bad_url)
            msg = str(exc_info.value)
            for pattern in forbidden:
                assert pattern.lower() not in msg.lower(), (
                    f"Error message leaked {pattern!r}"
                )


# ── Downgrade safety tests ──────────────────────────────────────────────────


@pytest.mark.no_sqlite_setup
class TestDowngradeSafety:
    """Verify the baseline downgrade cannot drop legacy tables."""

    def test_downgrade_raises_runtime_error(self, unique_db):
        run_alembic_upgrade(unique_db)
        with pytest.raises(RuntimeError, match=r"(?i)forward-only"):
            run_alembic_downgrade(unique_db)

    def test_tables_survive_failed_downgrade(self, unique_db):
        run_alembic_upgrade(unique_db)
        with pytest.raises(RuntimeError, match=r"(?i)forward-only"):
            run_alembic_downgrade(unique_db)
        engine = create_engine(unique_db)
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        missing = EXPECTED_TABLES - tables
        assert not missing, (
            f"Tables dropped by failed downgrade: {missing}"
        )