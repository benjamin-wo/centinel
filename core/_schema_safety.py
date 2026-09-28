"""Schema safety guard shared between alembic/env.py and tests.

``reject_unsafe_url()`` validates both the host and the database name.
Only local Unix-socket / localhost connections targeting a database whose
name matches the disposable test pattern (``np_baseline_test_*``) are
permitted.  This prevents accidental migration against a production-like
or pre-existing local database.
"""

import re
from sqlalchemy.engine.url import make_url

# Only database names matching this pattern are accepted.
# The test harness in test_migration_baseline.py creates databases named
# ``np_baseline_test_<12-hex-chars>``.
_ALLOWED_DB_PATTERN = re.compile(r"^np_baseline_test_[0-9a-f]{12}$")

# Database names that are explicitly forbidden even if they match the pattern.
# (Reserved local system databases, production names, project databases.)
_FORBIDDEN_DB_NAMES: frozenset[str] = frozenset({
    "postgres",
    "production",
    "proddb",
    "prod",
    "nexus-prime",
    "nexus_prime",
    "template0",
    "template1",
})


def reject_unsafe_url(url: str) -> None:
    """Raise RuntimeError if *url* targets an unsafe host or database name.

    Safety rules (both must pass):
      1. Host must be a local Unix socket, ``localhost``, or ``127.0.0.1``.
      2. Database name must match the disposable test pattern
         ``np_baseline_test_<12-hex-chars>`` and must not be a forbidden
         reserved name.

    The error message intentionally avoids printing the URL, username,
    password, or hostname.
    """
    parsed = make_url(url)
    host = (parsed.host or "").strip().lower()
    db_name = (parsed.database or "").strip()

    # ── Host check ──────────────────────────────────────────────────────
    host_ok = (
        not host
        or host in ("localhost", "127.0.0.1", "::1")
        or host.startswith("/")
    )
    if not host_ok:
        raise RuntimeError(
            "Refusing to migrate a non-local database target. "
            "Alembic operations are restricted to local Unix-socket or "
            "localhost connections.  Use the test harness with a disposable "
            "local PostgreSQL database for development and CI."
        )

    # ── Database name check ─────────────────────────────────────────────
    if not db_name:
        raise RuntimeError(
            "Refusing to migrate without an explicit database name. "
            "Alembic operations require a named disposable test database."
        )

    if db_name.lower() in _FORBIDDEN_DB_NAMES:
        raise RuntimeError(
            "Refusing to migrate a reserved or pre-existing database. "
            "Alembic operations require a disposable test database "
            "created by the test harness."
        )

    if not _ALLOWED_DB_PATTERN.match(db_name):
        raise RuntimeError(
            "Refusing to migrate an unmarked local database. "
            "Alembic operations require a disposable test database "
            "created by the test harness."
        )