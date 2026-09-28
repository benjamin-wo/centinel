# Centinel — Finance Agent

A **finance-focused agentic assistant** deployed on **Railway**, living on **Telegram** and a
**web cockpit/dashboard**. One tool-chaining agent fulfils expense and finance requests using
**skills declared as markdown files with frontmatter** — adding a skill means dropping a folder,
no code changes.

> Ported from `nexus-prime` — see [`PORTING.md`](PORTING.md) for the migration record.

## Quick Start

```bash
# Install dependencies
uv sync

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run tests
pytest tests/ -v

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Documentation

- [Architecture Glossary](CONTEXT.md)
- [Design System](DESIGN.md)
- [Wayfinder Map](map.md)