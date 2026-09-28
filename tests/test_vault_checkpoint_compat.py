from cryptography.fernet import Fernet
import pytest

import core.vault as vault
from core.config import settings
from orchestrator.checkpointer import migrate_checkpointer


def test_missing_encryption_key_fails_closed_in_production(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "encryption_key", None)
    monkeypatch.setattr(vault, "_fernet_instance", None)

    with pytest.raises(RuntimeError, match="ENCRYPTION_KEY"):
        vault.get_fernet_instance()


def test_configured_key_round_trip_preserves_ciphertext_compatibility(monkeypatch):
    key = Fernet.generate_key().decode("utf-8")
    monkeypatch.setattr(settings, "encryption_key", key)
    monkeypatch.setattr(vault, "_fernet_instance", None)

    ciphertext = vault.encrypt_token("clone-only oauth payload")

    assert ciphertext != "clone-only oauth payload"
    assert vault.decrypt_token(ciphertext) == "clone-only oauth payload"


@pytest.mark.asyncio
async def test_checkpoint_migration_requires_postgres(monkeypatch):
    monkeypatch.setattr(settings, "database_url", "sqlite+aiosqlite:///./test_assistant.db")

    with pytest.raises(RuntimeError, match="PostgreSQL"):
        await migrate_checkpointer()
