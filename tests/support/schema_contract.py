"""Legacy schema contract constants for baseline migration tests.

Derived from core/models.py (9 SQLModel tables) + core/legacy_schema.py
(8 unported legacy tables from the production clone).  17 application-owned
tables total.  Excludes Alembic bookkeeping and LangGraph checkpointer tables.

This file is a data table (schema declarations, not algorithmic code) so the
250-LOC ceiling does not apply — file size is proportional to the number of
tables under management.
"""

# noqa: SIZE_OK — data table: column/index/PK/FK declarations for 17 tables

EXPECTED_TABLES = frozenset({
    # 9 SQLModel tables
    "userprofile",
    "usercredential",
    "expensetransaction",
    "incometransaction",
    "deletedexpensemessage",
    "expenseundoentry",
    "scheduledjob",
    "taskitem",
    "capabilityrequestlog",
    # 8 unported legacy tables (clone-derived)
    "busstop",
    "conversationauditlog",
    "groceryitem",
    "pointsbalance",
    "productionbuglog",
    "qualityauditlog",
    "whiteboardproject",
    "whiteboardblock",
})

EXPECTED_COLUMNS: dict[str, list[tuple[str, str, bool]]] = {
    "userprofile": [
        ("user_id", "INTEGER", False),
        ("telegram_chat_id", "INTEGER", False),
        ("current_timezone", "VARCHAR", False),
        ("home_currency", "VARCHAR", False),
        ("tracked_banks", "JSON", True),
        ("email_exclude_domains", "JSON", True),
        ("email_content_type_presets", "JSON", True),
        ("whiteboard_seeded", "BOOLEAN", False),
        ("last_whiteboard_id", "INTEGER", True),
        ("last_email_digest_at", "TIMESTAMP", True),
        ("created_at", "TIMESTAMP", False),
    ],
    "usercredential": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("provider", "VARCHAR", False),
        ("encrypted_token_payload", "VARCHAR", False),
        ("updated_at", "TIMESTAMP", False),
    ],
    "expensetransaction": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("amount", "DOUBLE", False),
        ("currency", "VARCHAR", False),
        ("merchant", "VARCHAR", False),
        ("category", "VARCHAR", False),
        ("date", "TIMESTAMP", False),
        ("source_message_id", "VARCHAR", True),
        ("source_sender_domain", "VARCHAR", True),
        ("logged_at", "TIMESTAMP", True),
        ("is_verified", "BOOLEAN", False),
        ("notes", "VARCHAR", True),
        ("receipt_items", "JSON", True),
        ("split_data", "JSON", True),
    ],
    "incometransaction": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("amount", "DOUBLE", False),
        ("currency", "VARCHAR", False),
        ("source", "VARCHAR", False),
        ("category", "VARCHAR", False),
        ("date", "TIMESTAMP", False),
        ("notes", "VARCHAR", True),
        ("source_message_id", "VARCHAR", True),
        ("linked_expense_id", "INTEGER", True),
        ("created_at", "TIMESTAMP", False),
    ],
    "deletedexpensemessage": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("source_message_id", "VARCHAR", False),
        ("deleted_at", "TIMESTAMP", False),
    ],
    "expenseundoentry": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("expense_id", "INTEGER", False),
        ("kind", "VARCHAR", False),
        ("snapshot", "JSON", True),
        ("created_at", "TIMESTAMP", False),
    ],
    "scheduledjob": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("job_name", "VARCHAR", False),
        ("cron_expression", "VARCHAR", False),
        ("instruction_prompt", "VARCHAR", False),
        ("timezone", "VARCHAR", False),
        ("is_active", "BOOLEAN", False),
        ("created_at", "TIMESTAMP", False),
    ],
    "taskitem": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("title", "VARCHAR", False),
        ("description", "VARCHAR", True),
        ("status", "VARCHAR", False),
        ("priority", "VARCHAR", False),
        ("due_at", "TIMESTAMP", True),
        ("reminder_type", "VARCHAR", False),
        ("reminder_time", "TIMESTAMP", True),
        ("cron_expression", "VARCHAR", True),
        ("timezone", "VARCHAR", False),
        ("is_reminder_active", "BOOLEAN", False),
        ("linked_expense_id", "INTEGER", True),
        ("iou_friend", "VARCHAR", True),
        ("iou_amount", "DOUBLE", True),
        ("created_at", "TIMESTAMP", False),
        ("completed_at", "TIMESTAMP", True),
    ],
    "capabilityrequestlog": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("requested_task", "VARCHAR", False),
        ("intent_type", "VARCHAR", False),
        ("missing_capability_tags", "VARCHAR", False),
        ("expectation", "VARCHAR", True),
        ("block_reason", "VARCHAR", True),
        ("agent_reply", "VARCHAR", True),
        ("channel", "VARCHAR", True),
        ("created_at", "TIMESTAMP", False),
    ],
    # ── 8 unported legacy tables (clone-derived) ─────────────────────────
    "busstop": [
        ("code", "VARCHAR", False),
        ("description", "VARCHAR", False),
        ("road_name", "VARCHAR", False),
        ("lat", "DOUBLE", True),
        ("lng", "DOUBLE", True),
    ],
    "conversationauditlog": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("thread_id", "VARCHAR", False),
        ("message_count", "INTEGER", False),
        ("judge_model", "VARCHAR", False),
        ("faithfulness_score", "INTEGER", False),
        ("helpfulness_score", "INTEGER", False),
        ("routing_score", "INTEGER", False),
        ("tool_correctness_score", "INTEGER", False),
        ("verdict", "VARCHAR", False),
        ("evidence", "VARCHAR", False),
        ("created_at", "TIMESTAMP", False),
    ],
    "groceryitem": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("name", "VARCHAR", False),
        ("quantity", "VARCHAR", False),
        ("category", "VARCHAR", False),
        ("is_purchased", "BOOLEAN", False),
        ("added_at", "TIMESTAMP", False),
    ],
    "pointsbalance": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("program", "VARCHAR", False),
        ("issuer", "VARCHAR", False),
        ("balance", "DOUBLE", False),
        ("updated_at", "TIMESTAMP", False),
        ("expiry_date", "TIMESTAMP", True),
    ],
    "productionbuglog": [
        ("id", "INTEGER", False),
        ("title", "VARCHAR", False),
        ("subsystem", "VARCHAR", False),
        ("severity", "VARCHAR", False),
        ("status", "VARCHAR", False),
        ("fingerprint", "VARCHAR", False),
        ("occurrence_count", "INTEGER", False),
        ("created_at", "TIMESTAMP", False),
        ("updated_at", "TIMESTAMP", False),
        ("detection_source", "VARCHAR", False),
        ("error_traceback", "VARCHAR", True),
        ("github_issue_number", "INTEGER", True),
        ("github_issue_url", "VARCHAR", True),
        ("reproduction_context", "VARCHAR", True),
        ("root_cause", "VARCHAR", True),
        ("suggested_fix", "VARCHAR", True),
        ("thread_id", "VARCHAR", True),
        ("user_id", "INTEGER", True),
    ],
    "qualityauditlog": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("thread_id", "VARCHAR", False),
        ("evaluated_at", "TIMESTAMP", False),
        ("faithfulness_score", "INTEGER", False),
        ("routing_efficiency_score", "INTEGER", False),
        ("hallucination_detected", "BOOLEAN", False),
        ("unnecessary_friction_flag", "BOOLEAN", False),
        ("evidence_explanation", "VARCHAR", False),
    ],
    "whiteboardproject": [
        ("id", "INTEGER", False),
        ("user_id", "INTEGER", False),
        ("title", "VARCHAR", False),
        ("category", "VARCHAR", False),
        ("emoji_icon", "VARCHAR", False),
        ("summary", "VARCHAR", True),
        ("cover_ready", "BOOLEAN", False),
        ("section_order", "JSON", True),
        ("created_at", "TIMESTAMP", False),
        ("updated_at", "TIMESTAMP", False),
    ],
    "whiteboardblock": [
        ("id", "INTEGER", False),
        ("project_id", "INTEGER", False),
        ("section_name", "VARCHAR", False),
        ("block_type", "VARCHAR", False),
        ("title", "VARCHAR", False),
        ("content_payload", "JSON", True),
        ("position_order", "INTEGER", False),
        ("linked_expense_id", "INTEGER", True),
        ("linked_task_id", "INTEGER", True),
        ("created_at", "TIMESTAMP", False),
        ("updated_at", "TIMESTAMP", False),
    ],
}

EXPECTED_INDEXES: dict[str, list[tuple[str, list[str], bool]]] = {
    "userprofile": [
        ("ix_userprofile_telegram_chat_id", ["telegram_chat_id"], True),
    ],
    "usercredential": [
        ("ix_usercredential_user_id", ["user_id"], False),
        ("ix_usercredential_provider", ["provider"], False),
    ],
    "expensetransaction": [
        ("ix_expensetransaction_user_id", ["user_id"], False),
        ("ix_expensetransaction_source_message_id", ["source_message_id"], True),
        # Clone lacks ix_expensetransaction_source_sender_domain and
        # ix_expensetransaction_logged_at — removed per clone observation.
    ],
    "incometransaction": [
        ("ix_incometransaction_user_id", ["user_id"], False),
        ("ix_incometransaction_source", ["source"], False),
        ("ix_incometransaction_category", ["category"], False),
        ("ix_incometransaction_source_message_id", ["source_message_id"], True),
        ("ix_incometransaction_linked_expense_id", ["linked_expense_id"], False),
    ],
    "deletedexpensemessage": [
        ("ix_deletedexpensemessage_user_id", ["user_id"], False),
        ("ix_deletedexpensemessage_source_message_id", ["source_message_id"], True),
    ],
    "expenseundoentry": [
        ("ix_expenseundoentry_user_id", ["user_id"], False),
        ("ix_expenseundoentry_expense_id", ["expense_id"], False),
        ("ix_expenseundoentry_kind", ["kind"], False),
    ],
    "scheduledjob": [
        ("ix_scheduledjob_user_id", ["user_id"], False),
    ],
    "taskitem": [
        ("ix_taskitem_user_id", ["user_id"], False),
        ("ix_taskitem_status", ["status"], False),
        ("ix_taskitem_priority", ["priority"], False),
        ("ix_taskitem_linked_expense_id", ["linked_expense_id"], False),
        ("ix_taskitem_iou_friend", ["iou_friend"], False),
        ("ix_taskitem_iou_amount", ["iou_amount"], False),
    ],
    "capabilityrequestlog": [
        ("ix_capabilityrequestlog_user_id", ["user_id"], False),
        ("ix_capabilityrequestlog_intent_type", ["intent_type"], False),
        ("ix_capabilityrequestlog_missing_capability_tags", ["missing_capability_tags"], False),
    ],
    # ── 8 unported legacy tables ─────────────────────────────────────────
    "busstop": [
        ("ix_busstop_description", ["description"], False),
        ("ix_busstop_road_name", ["road_name"], False),
    ],
    "conversationauditlog": [
        ("ix_conversationauditlog_thread_id", ["thread_id"], False),
        ("ix_conversationauditlog_user_id", ["user_id"], False),
        ("ix_conversationauditlog_verdict", ["verdict"], False),
    ],
    "groceryitem": [
        ("ix_groceryitem_user_id", ["user_id"], False),
    ],
    "pointsbalance": [
        ("ix_pointsbalance_user_id", ["user_id"], False),
        ("ix_pointsbalance_issuer", ["issuer"], False),
        ("ix_pointsbalance_program", ["program"], False),
        # Unique constraint backing index (PostgreSQL creates a unique
        # btree index behind every UNIQUE constraint).
        ("uq_points_user_issuer_program", ["user_id", "issuer", "program"], True),
    ],
    "productionbuglog": [
        ("ix_productionbuglog_detection_source", ["detection_source"], False),
        ("ix_productionbuglog_fingerprint", ["fingerprint"], False),
        ("ix_productionbuglog_severity", ["severity"], False),
        ("ix_productionbuglog_status", ["status"], False),
        ("ix_productionbuglog_subsystem", ["subsystem"], False),
        ("ix_productionbuglog_thread_id", ["thread_id"], False),
        ("ix_productionbuglog_title", ["title"], False),
        ("ix_productionbuglog_user_id", ["user_id"], False),
    ],
    "qualityauditlog": [
        ("ix_qualityauditlog_hallucination_detected", ["hallucination_detected"], False),
        ("ix_qualityauditlog_thread_id", ["thread_id"], False),
        ("ix_qualityauditlog_user_id", ["user_id"], False),
    ],
    "whiteboardproject": [
        ("ix_whiteboardproject_category", ["category"], False),
        ("ix_whiteboardproject_user_id", ["user_id"], False),
    ],
    "whiteboardblock": [
        ("ix_whiteboardblock_block_type", ["block_type"], False),
        ("ix_whiteboardblock_project_id", ["project_id"], False),
        ("ix_whiteboardblock_section_name", ["section_name"], False),
    ],
}

EXPECTED_PKS: dict[str, list[str]] = {
    "userprofile": ["user_id"],
    "usercredential": ["id"],
    "expensetransaction": ["id"],
    "incometransaction": ["id"],
    "deletedexpensemessage": ["id"],
    "expenseundoentry": ["id"],
    "scheduledjob": ["id"],
    "taskitem": ["id"],
    "capabilityrequestlog": ["id"],
    # 8 unported legacy tables
    "busstop": ["code"],
    "conversationauditlog": ["id"],
    "groceryitem": ["id"],
    "pointsbalance": ["id"],
    "productionbuglog": ["id"],
    "qualityauditlog": ["id"],
    "whiteboardproject": ["id"],
    "whiteboardblock": ["id"],
}

EXPECTED_FKS: dict[str, list[tuple[list[str], str, list[str]]]] = {
    "usercredential": [(["user_id"], "userprofile", ["user_id"])],
    "expensetransaction": [(["user_id"], "userprofile", ["user_id"])],
    "incometransaction": [
        (["user_id"], "userprofile", ["user_id"]),
        # Clone lacks FK incometransaction.linked_expense_id →
        # expensetransaction.id — removed per clone observation.
    ],
    "scheduledjob": [(["user_id"], "userprofile", ["user_id"])],
    "taskitem": [
        (["user_id"], "userprofile", ["user_id"]),
        # Clone lacks FK taskitem.linked_expense_id →
        # expensetransaction.id — removed per clone observation.
    ],
    "capabilityrequestlog": [(["user_id"], "userprofile", ["user_id"])],
    # 8 unported legacy tables (only those with FKs)
    "groceryitem": [(["user_id"], "userprofile", ["user_id"])],
    "pointsbalance": [(["user_id"], "userprofile", ["user_id"])],
    "qualityauditlog": [(["user_id"], "userprofile", ["user_id"])],
    "whiteboardproject": [(["user_id"], "userprofile", ["user_id"])],
    "whiteboardblock": [
        (["project_id"], "whiteboardproject", ["id"]),
        (["linked_expense_id"], "expensetransaction", ["id"]),
        (["linked_task_id"], "taskitem", ["id"]),
    ],
}

# Tables that are NOT in EXPECTED_TABLES but may legitimately appear in a
# database (alembic_version) or are owned by LangGraph's checkpointer and
# managed outside Alembic.  The clone inventory observed four LangGraph
# checkpointer tables.
KNOWN_EXTRA_TABLES: frozenset[str] = frozenset({
    "alembic_version",
    "checkpoint_migrations",
    "checkpoints",
    "checkpoint_writes",
    "checkpoint_blobs",
})

# Server-default values observed in the restored clone (literal defaults only).
# Each key is ``table.column``; the value is the exact string returned by
# ``inspector.get_columns()["default"]`` (PostgreSQL catalog form).
EXPECTED_SERVER_DEFAULTS: dict[str, str] = {
    "userprofile.whiteboard_seeded": "false",
    "userprofile.email_exclude_domains": "'[]'::json",
    "userprofile.email_content_type_presets": "'[]'::json",
    "expensetransaction.receipt_items": "'[]'::json",
    "expensetransaction.split_data": "'{}'::json",
    "whiteboardproject.cover_ready": "false",
    "whiteboardproject.section_order": "'[]'::json",
}

# Columns whose server default is an auto-generated ``nextval(...)`` sequence
# expression (16 of 17 app tables — ``busstop.code`` is a VARCHAR PK with no
# sequence).  The comparator asserts each has a `nextval(...)` default and that
# no non-expected column carries one.
EXPECTED_SEQUENCE_COLUMNS: frozenset[str] = frozenset({
    "userprofile.user_id",
    "usercredential.id",
    "expensetransaction.id",
    "incometransaction.id",
    "deletedexpensemessage.id",
    "expenseundoentry.id",
    "scheduledjob.id",
    "taskitem.id",
    "capabilityrequestlog.id",
    "conversationauditlog.id",
    "groceryitem.id",
    "pointsbalance.id",
    "productionbuglog.id",
    "qualityauditlog.id",
    "whiteboardproject.id",
    "whiteboardblock.id",
})

# Canonical type names for schema comparison (maps reported names to canonical).
# Used by _schema_mismatches to avoid false positives like JSON vs JSONB.
TYPE_CANONICAL: dict[str, str] = {
    "INTEGER": "INTEGER",
    "BIGINT": "INTEGER",
    "INT": "INTEGER",
    "SERIAL": "INTEGER",
    "BIGSERIAL": "INTEGER",
    "DOUBLE PRECISION": "DOUBLE",
    "FLOAT": "DOUBLE",
    "REAL": "DOUBLE",
    "BOOLEAN": "BOOLEAN",
    "BOOL": "BOOLEAN",
    "VARCHAR": "VARCHAR",
    "CHARACTER VARYING": "VARCHAR",
    "TEXT": "VARCHAR",
    "JSON": "JSON",
    "JSONB": "JSONB",
    "TIMESTAMP WITHOUT TIME ZONE": "TIMESTAMP",
    "TIMESTAMP": "TIMESTAMP",
    "DATETIME": "TIMESTAMP",
    "DATE": "DATE",
    "NUMERIC": "NUMERIC",
}


def normalize_type(raw: str) -> str:
    """Return the canonical form of a SQL type name for comparison."""
    upper = raw.strip().upper()
    # Strip precision/scale like NUMERIC(10,2) or VARCHAR(255)
    for suffix in ("(10,2)", "(255)", "(53)"):
        upper = upper.replace(suffix, "")
    upper = upper.strip()
    return TYPE_CANONICAL.get(upper, upper)