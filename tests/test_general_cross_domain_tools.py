"""Cross-domain read tools for GeneralPlugin: part of making "general" a real
conversational agent (full history + tools, the default landing zone for
ambiguous/cross-domain asks) rather than one narrow capability among many
that only ever sees the latest message. Deliberately READ-only -- writes
stay behind their own guarded plugin (expenses).

Installed skills: email, expenses, web-research. Removed tests for absent
capabilities: routes, whiteboard, memory, code-exec.
"""
import pytest
from langchain_core.messages import HumanMessage

from core.db import async_session_factory, init_db
from core.models import ScheduledJob, UserProfile
from capabilities.general.tools import (
    list_my_reminders,
    search_my_email,
)


@pytest.fixture(autouse=True)
async def ensure_db():
    await init_db()


@pytest.mark.asyncio
async def test_list_my_reminders_reports_active_jobs():
    async with async_session_factory() as session:
        session.add(UserProfile(user_id=9101, telegram_chat_id=9101))
        session.add(ScheduledJob(
            user_id=9101,
            job_name="Weekly grocery reminder",
            cron_expression="0 9 * * 1",
            instruction_prompt="remind me to buy groceries",
        ))
        session.add(ScheduledJob(
            user_id=9101,
            job_name="Inactive job, should not appear",
            cron_expression="0 9 * * 1",
            instruction_prompt="stale",
            is_active=False,
        ))
        await session.commit()

    result = await list_my_reminders.ainvoke({"user_id": 9101})
    assert "Weekly grocery reminder" in result
    assert "Inactive job" not in result


@pytest.mark.asyncio
async def test_list_my_reminders_reports_none_when_empty():
    result = await list_my_reminders.ainvoke({"user_id": 9102})
    assert "No active reminders" in result


@pytest.mark.asyncio
async def test_search_my_email_formats_results(monkeypatch):
    import capabilities.email.tools as email_tools

    async def fake_search(user_id, custom_query=None, provider=None, latest=False):
        assert user_id == 9105
        return [{"sender": "flights@airline.com", "subject": "Your booking confirmation", "date": "2026-08-20"}]

    monkeypatch.setattr(email_tools, "search_email_messages", fake_search)

    result = await search_my_email.ainvoke({"query": "flight", "user_id": 9105})
    assert "flights@airline.com" in result
    assert "Your booking confirmation" in result


@pytest.mark.asyncio
async def test_search_my_email_reports_none_found(monkeypatch):
    import capabilities.email.tools as email_tools

    async def fake_search(user_id, custom_query=None, provider=None, latest=False):
        return []

    monkeypatch.setattr(email_tools, "search_email_messages", fake_search)

    result = await search_my_email.ainvoke({"query": "", "latest": True, "user_id": 9106})
    assert "No matching messages" in result


@pytest.mark.asyncio
async def test_general_plugin_agent_calls_email_tool(monkeypatch):
    """The orchestrator agent can answer an email-search ask directly via its tools."""
    from langchain_core.messages import AIMessage as _AIMessage

    from orchestrator.agent_loop import agent_loop
    import orchestrator.agent_loop as agent_loop_module

    class _FakeEmailTool:
        name = "search_my_email"

        async def ainvoke(self, args):
            return "• flights@airline.com — Your booking confirmation (2026-08-20)"

    class _FakeToolCallingLLM:
        def __init__(self):
            self.calls = 0

        def bind_tools(self, tools):
            self.tools = tools
            return self

        async def ainvoke(self, messages):
            self.calls += 1
            if self.calls == 1:
                return _AIMessage(content="", tool_calls=[{
                    "name": "search_my_email",
                    "args": {"query": "flight booking", "user_id": 9108},
                    "id": "call_email_1",
                    "type": "tool_call",
                }])
            return _AIMessage(content="I found a booking confirmation from flights@airline.com.")

    import capabilities.general.tools as general_tools

    monkeypatch.setattr(general_tools, "search_my_email", _FakeEmailTool())
    monkeypatch.setattr(agent_loop_module, "get_agent_llm", lambda *a, **k: _FakeToolCallingLLM())
    monkeypatch.setattr(agent_loop_module.settings, "gemini_api_key", "fake-key-for-test")

    command = await agent_loop({
        "user_id": 9108,
        "messages": [HumanMessage(content="find my flight booking email")],
    })

    reply_messages = command.update["messages"]
    assert "booking confirmation" in str(reply_messages[-1].content)
    tool_call_messages = [m for m in reply_messages if isinstance(m, _AIMessage) and m.tool_calls]
    assert tool_call_messages and tool_call_messages[0].tool_calls[0]["name"] == "search_my_email"


@pytest.mark.asyncio
async def test_general_plugin_binds_and_guards_all_cross_domain_tools(monkeypatch):
    """The bounded tool loop must include the cross-domain read tools declared
    by installed skills, and each identity_bound tool must override a model-
    supplied user_id (never trust it). Exercises the real
    core.tool_guard.identity_bound path end-to-end via bind_user_id, not an
    introspection shortcut."""
    from core.tool_guard import bind_user_id, current_user_id
    from orchestrator.agent_loop import _build_tool_roster, _visible_skills

    tools_by_name = {t.name: t for t in _build_tool_roster(_visible_skills(True))}
    # Current installed skills: email, expenses, web-research
    # search_my_email is declared by email skill and is identity_bound
    assert "search_my_email" in tools_by_name, "search_my_email must be bound in agent_loop's tool roster"
    assert "search_web" in tools_by_name, "search_web must be bound in agent_loop's tool roster"
    assert "fetch_url" in tools_by_name, "fetch_url must be bound in agent_loop's tool roster"
    # Undeclared tools (list_my_reminders, get_bus_timings, etc.) are NOT in the roster
    assert "list_my_reminders" not in tools_by_name, (
        "list_my_reminders is not declared by any installed skill"
    )
    assert "get_bus_timings" not in tools_by_name, (
        "get_bus_timings is not declared by any installed skill (routes removed)"
    )

    captured: dict = {}

    async def _spy_search_email(user_id, custom_query=None, provider=None, latest=False):
        captured["user_id"] = user_id
        return []

    monkeypatch.setattr("capabilities.email.tools.search_email_messages", _spy_search_email)

    token = bind_user_id(9111)
    try:
        await tools_by_name["search_my_email"].ainvoke({"query": "test", "user_id": 666666})
    finally:
        current_user_id.reset(token)

    assert captured["user_id"] == 9111, "identity_bound must override the model-supplied user_id"
    assert captured["user_id"] != 666666


@pytest.mark.asyncio
async def test_general_plugin_surfaces_tool_call_provenance_for_persistence(monkeypatch):
    """Regression (#53): the tool loop must persist real AIMessage(tool_calls)
    and ToolMessage pairs into checkpointed state alongside the final reply,
    so the durable conversation transcript shows tool invocation provenance
    instead of being indistinguishable from a hallucination."""
    from langchain_core.messages import AIMessage, ToolMessage
    import orchestrator.agent_loop as agent_loop_module
    from orchestrator.agent_loop import agent_loop

    class _SpySearchEmail:
        name = "search_my_email"

        async def ainvoke(self, args):
            return "• noreply@bank.com — Monthly statement (2026-09-01)"

    class _FakeToolCallingLLM:
        def __init__(self):
            self.calls = 0

        def bind_tools(self, tools):
            return self

        async def ainvoke(self, messages):
            self.calls += 1
            if self.calls == 1:
                return AIMessage(content="", tool_calls=[{
                    "name": "search_my_email",
                    "args": {"query": "bank statement", "user_id": 9108},
                    "id": "call_1",
                    "type": "tool_call",
                }])
            return AIMessage(content="Here's your bank statement email.")

    import capabilities.general.tools as general_tools

    monkeypatch.setattr(general_tools, "search_my_email", _SpySearchEmail())
    monkeypatch.setattr(agent_loop_module, "get_agent_llm", lambda *a, **k: _FakeToolCallingLLM())
    monkeypatch.setattr(agent_loop_module.settings, "gemini_api_key", "fake-key-for-test")

    command = await agent_loop({
        "user_id": 9108,
        "messages": [HumanMessage(content="find my bank statement email")],
    })

    persisted = command.update["messages"]
    assert "Here's your bank statement email" in str(persisted[-1].content)
    # The real tool call/result must be surfaced, not silently dropped.
    tool_call_messages = [m for m in persisted if isinstance(m, AIMessage) and m.tool_calls]
    tool_result_messages = [m for m in persisted if isinstance(m, ToolMessage)]
    assert tool_call_messages, "the tool-calling AIMessage must be persisted"
    assert tool_call_messages[0].tool_calls[0]["name"] == "search_my_email"
    assert tool_result_messages, "the ToolMessage result must be persisted"
    assert "noreply@bank.com" in str(tool_result_messages[0].content)
