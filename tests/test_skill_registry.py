"""The skill registry: SKILL.md frontmatter is the authoring surface."""
import textwrap
from pathlib import Path

from core.skill_registry import (
    build_tool_registry,
    discover_skills,
    load_skill_file,
    make_load_skill_tool,
    parse_frontmatter,
    resolve_skill_tools,
    skill_index_text,
)


def test_parse_frontmatter_basic():
    data, body = parse_frontmatter(
        "---\nname: transit\ndescription: Live bus times\ntools:\n  - get_bus_timings\n---\n\n# Body here\n"
    )
    assert data["name"] == "transit"
    assert data["tools"] == ["get_bus_timings"]
    assert "# Body here" in body


def test_parse_frontmatter_missing_returns_empty():
    data, body = parse_frontmatter("# just markdown\nno frontmatter")
    assert data == {}
    assert "no frontmatter" in body


def test_load_skill_file(tmp_path: Path):
    skill_dir = tmp_path / "transit"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        textwrap.dedent(
            """\
            ---
            name: transit
            description: Live Singapore bus times
            tags: [transit, bus]
            side_effect: read
            tools:
              - get_bus_timings
              - not_a_real_tool
            ---

            # How to answer bus asks
            """
        )
    )
    skill = load_skill_file(skill_dir / "SKILL.md")
    assert skill is not None
    assert skill.name == "transit"
    assert skill.side_effect == "read"
    assert skill.tools == ("get_bus_timings", "not_a_real_tool")
    assert "How to answer bus asks" in skill.body


def test_discover_skills_from_repo():
    skills = discover_skills()
    names = set(skills)
    assert {"web-research", "expenses", "email"} == names, (
        f"expected exactly [email, expenses, web-research], got {sorted(names)}"
    )


def test_tool_registry_resolves_all_declared_skills():
    registry = build_tool_registry()
    # Tools declared by the three installed skills (email, expenses, web-research)
    # plus tools registered in TOOL_MODULES (capabilities.general/email/expenses)
    for name in (
        "search_web", "fetch_url", "search_my_email",
        "process_extracted_expense", "record_incoming_money",
        "query_transactions", "get_user_expenses", "sweep_email_for_expenses",
    ):
        assert name in registry, name

    skills = discover_skills()
    # Check that tools declared by a known skill resolve to callables
    email_tools = resolve_skill_tools(skills["email"])
    email_names = {t.name for t in email_tools}
    assert "search_my_email" in email_names
    assert "sweep_email_for_expenses" in email_names

    expenses_tools = resolve_skill_tools(skills["expenses"])
    expenses_names = {t.name for t in expenses_tools}
    assert "process_extracted_expense" in expenses_names
    assert "get_user_expenses" in expenses_names
    assert "query_transactions" in expenses_names


def test_skill_index_lists_every_skill():
    skills = discover_skills()
    index = skill_index_text(skills)
    for name in skills:
        assert name in index


def test_load_skill_tool_returns_body():
    skills = discover_skills()
    tool = make_load_skill_tool(lambda: skills)
    result = tool.invoke({"name": "email"})
    assert "Search the user's connected Gmail/Outlook" in result
    assert "sweep_email_for_expenses" in result

    miss = tool.invoke({"name": "does-not-exist"})
    assert "No skill named" in miss


def test_skill_side_effect_defaults_to_read(tmp_path: Path):
    skill_dir = tmp_path / "mystery"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\nname: mystery\ndescription: no side effect declared\n---\nbody")
    skill = load_skill_file(skill_dir / "SKILL.md")
    assert skill.side_effect == "read"
