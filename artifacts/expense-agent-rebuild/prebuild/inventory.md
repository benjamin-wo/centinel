# Prebuild Checkpoint Inventory

Date: 2026-09-28
Original checkout: `/Users/benjaminwo/Documents/centinel`
Checkpoint worktree: `/Users/benjaminwo/Documents/centinel-expense-agent-rebuild`

## Original Checkout Classification

- `pyproject.toml`: in-scope dependency compatibility change made during the prebuild gate.
- `uv.lock`: in-scope lockfile refresh corresponding to `pyproject.toml`.
- `expense-agent-rebuild.md`: preserved untracked user-provided work plan; not copied into the checkpoint commit.
- `.omo/`: preserved untracked orchestration artifacts; not copied into the checkpoint commit.

The original checkout was not reset, cleaned, stashed, or overwritten.

## Checkpoint Scope

The checkpoint contains only the dependency compatibility changes needed for the documented test suite:

- `pyproject.toml`
- `uv.lock`

No production data, credentials, screenshots, database dumps, or Railway state were included.
