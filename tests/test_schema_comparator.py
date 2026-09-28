"""Negative tests: schema comparator mutation detection.

Each test gets its own unique disposable PostgreSQL database to ensure
isolation when tests mutate the schema.
"""

import pytest
from sqlalchemy import create_engine, text
from tests.support.alembic_helpers import (
    run_alembic_upgrade,
    schema_mismatches,
)


@pytest.mark.no_sqlite_setup
class TestComparatorNegative:
    """Prove the schema comparator rejects every form of drift."""

    def test_missing_column_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE expensetransaction DROP COLUMN notes"))
            conn.commit()

        errors = schema_mismatches(unique_db)
        assert any("notes" in e for e in errors), (
            f"Expected notes mismatch, got: {errors}"
        )

    def test_missing_index_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            conn.execute(text("DROP INDEX IF EXISTS ix_expensetransaction_user_id"))
            conn.commit()
        errors = schema_mismatches(unique_db)
        assert any("ix_expensetransaction_user_id" in e for e in errors), (
            f"Expected ix_expensetransaction_user_id mismatch, got: {errors}"
        )

    def test_unexpected_column_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            conn.execute(
                text("ALTER TABLE expensetransaction ADD COLUMN rogue_col VARCHAR")
            )
            conn.commit()
        errors = schema_mismatches(unique_db)
        assert any("unexpected column" in e and "rogue_col" in e for e in errors), (
            f"Expected rogue_col mismatch, got: {errors}"
        )

    def test_unexpected_table_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            conn.execute(
                text("CREATE TABLE rogue_t (id INTEGER PRIMARY KEY, n VARCHAR)")
            )
            conn.commit()
        errors = schema_mismatches(unique_db)
        assert any("unexpected table" in e and "rogue_t" in e for e in errors), (
            f"Expected rogue_t mismatch, got: {errors}"
        )

    def test_primary_key_mismatch_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            # CASCADE because whiteboardblock FK depends on taskitem_pkey.
            conn.execute(
                text("ALTER TABLE taskitem DROP CONSTRAINT taskitem_pkey CASCADE")
            )
            conn.execute(
                text("ALTER TABLE taskitem "
                     "ADD CONSTRAINT taskitem_pkey PRIMARY KEY (id, user_id)")
            )
            conn.commit()
        errors = schema_mismatches(unique_db)
        assert any("PK" in e and "taskitem" in e for e in errors), (
            f"Expected taskitem PK mismatch, got: {errors}"
        )

    def test_foreign_key_mismatch_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            conn.execute(
                text("ALTER TABLE capabilityrequestlog "
                     "DROP CONSTRAINT fk_capabilityrequestlog_user_id_userprofile")
            )
            conn.commit()
        errors = schema_mismatches(unique_db)
        assert any("FK" in e and "capabilityrequestlog" in e for e in errors), (
            f"Expected capabilityrequestlog FK mismatch, got: {errors}"
        )

    def test_changed_column_type_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            conn.execute(
                text("ALTER TABLE expensetransaction "
                     "ALTER COLUMN split_data TYPE JSONB "
                     "USING split_data::jsonb")
            )
            conn.commit()
        errors = schema_mismatches(unique_db)
        assert any("split_data" in e and "JSON" in e for e in errors), (
            f"Expected split_data type-change mismatch, got: {errors}"
        )

    def test_missing_default_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            conn.execute(
                text("ALTER TABLE expensetransaction "
                     "ALTER COLUMN receipt_items DROP DEFAULT")
            )
            conn.commit()
        errors = schema_mismatches(unique_db)
        assert any("receipt_items" in e and "missing expected default" in e
                   for e in errors), (
            f"Expected receipt_items default mismatch, got: {errors}"
        )

    def test_unexpected_default_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            conn.execute(
                text("ALTER TABLE userprofile "
                     "ALTER COLUMN created_at "
                     "SET DEFAULT '1970-01-01 00:00:00'::timestamp")
            )
            conn.commit()
        errors = schema_mismatches(unique_db)
        assert any("created_at" in e and "unexpected default" in e
                   for e in errors), (
            f"Expected created_at unexpected default, got: {errors}"
        )

    def test_missing_sequence_default_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            conn.execute(
                text("ALTER TABLE usercredential "
                     "ALTER COLUMN id DROP DEFAULT")
            )
            conn.commit()
        errors = schema_mismatches(unique_db)
        assert any("usercredential.id" in e
                   and "missing expected sequence default" in e
                   for e in errors), (
            f"Expected usercredential.id sequence default mismatch, "
            f"got: {errors}"
        )

    def test_unexpected_sequence_default_is_detected(self, unique_db):
        run_alembic_upgrade(unique_db)
        engine = create_engine(unique_db)
        with engine.connect() as conn:
            conn.execute(
                text("CREATE SEQUENCE IF NOT EXISTS rogue_seq START 1")
            )
            conn.execute(
                text("ALTER TABLE userprofile "
                     "ALTER COLUMN home_currency "
                     "SET DEFAULT nextval('rogue_seq')")
            )
            conn.commit()
        errors = schema_mismatches(unique_db)
        assert any("userprofile.home_currency" in e
                   and "unexpected sequence default" in e
                   for e in errors), (
            f"Expected unexpected sequence default on home_currency, "
            f"got: {errors}"
        )