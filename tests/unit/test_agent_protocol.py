"""Tests for agents/protocol.py — TC-RH04 inter-agent messaging."""

from __future__ import annotations

from pathlib import Path

from plugin_examples.agents.context import SharedContext
from plugin_examples.agents.protocol import AgentMessage, MessageBus, MessageType


class TestMessageBus:
    def test_post_and_retrieve(self):
        bus = MessageBus()
        msg = AgentMessage(sender="agent-a", msg_type=MessageType.INFORM, payload={"key": "val"})
        bus.post(msg)
        assert bus.count == 1
        msgs = bus.get_messages()
        assert len(msgs) == 1
        assert msgs[0].sender == "agent-a"

    def test_filter_by_recipient(self):
        bus = MessageBus()
        bus.post(AgentMessage(sender="a", msg_type=MessageType.INFORM, recipient="b"))
        bus.post(AgentMessage(sender="a", msg_type=MessageType.INFORM, recipient="c"))
        bus.post(AgentMessage(sender="a", msg_type=MessageType.INFORM))  # broadcast
        msgs = bus.get_messages(recipient="b")
        assert len(msgs) == 2  # targeted + broadcast

    def test_filter_by_type(self):
        bus = MessageBus()
        bus.post(AgentMessage(sender="a", msg_type=MessageType.CLAIM))
        bus.post(AgentMessage(sender="a", msg_type=MessageType.YIELD))
        bus.post(AgentMessage(sender="a", msg_type=MessageType.CLAIM))
        claims = bus.get_messages(msg_type=MessageType.CLAIM)
        assert len(claims) == 2

    def test_clear(self):
        bus = MessageBus()
        bus.post(AgentMessage(sender="a", msg_type=MessageType.INFORM))
        bus.clear()
        assert bus.count == 0

    def test_to_list_serialization(self):
        bus = MessageBus()
        bus.post(AgentMessage(sender="a", msg_type=MessageType.REQUEST_INFO, payload={"q": 1}))
        data = bus.to_list()
        assert len(data) == 1
        assert data[0]["sender"] == "a"
        assert data[0]["msg_type"] == "REQUEST_INFO"
        assert data[0]["payload"] == {"q": 1}

    def test_message_timestamp_auto(self):
        msg = AgentMessage(sender="a", msg_type=MessageType.INFORM)
        assert msg.timestamp != ""

    def test_message_types_enum(self):
        assert MessageType.CLAIM.value == "CLAIM"
        assert MessageType.YIELD.value == "YIELD"
        assert MessageType.INFORM.value == "INFORM"
        assert MessageType.REQUEST_INFO.value == "REQUEST_INFO"


class TestSharedContextMessageBus:
    def test_post_and_get_messages(self, tmp_path: Path):
        ctx = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path)
        ctx.post_message("agent-1", MessageType.CLAIM, {"action": "nuget_fetch"})
        ctx.post_message("agent-2", MessageType.YIELD, recipient="agent-1")
        msgs = ctx.get_messages(recipient="agent-1")
        assert len(msgs) == 2  # claim (broadcast) + yield (targeted)

    def test_bus_isolated_per_context(self, tmp_path: Path):
        ctx1 = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path)
        ctx2 = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path)
        ctx1.post_message("a", MessageType.INFORM)
        assert ctx1.message_bus.count == 1
        assert ctx2.message_bus.count == 0

    def test_default_bus_is_empty(self, tmp_path: Path):
        ctx = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path)
        assert ctx.message_bus.count == 0
        assert ctx.get_messages() == []


class TestBuiltinAgentsPostMessages:
    """Verify that builtin agents use the message bus during execution."""

    def test_conservation_agent_posts_inform(self, tmp_path: Path):
        from unittest.mock import patch

        ctx = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path)
        from plugin_examples.agents.builtin import ConservationCheckAgent

        agent = ConservationCheckAgent()
        with patch("plugin_examples.portfolio_action_planner._load_denominators", return_value={}), \
             patch("plugin_examples.portfolio_action_planner._count_contracts", return_value={}):
            agent.execute(ctx, "PORTFOLIO_CONSERVATION_CHECK")
        msgs = ctx.get_messages(msg_type=MessageType.INFORM)
        assert len(msgs) >= 1
        assert msgs[0].sender == "conservation_check"

    def test_version_drift_agent_posts_inform(self, tmp_path: Path):
        from unittest.mock import patch

        ctx = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path)
        from plugin_examples.agents.builtin import VersionDriftAgent

        agent = VersionDriftAgent()
        with patch("plugin_examples.portfolio_action_planner._load_denominators", return_value={}):
            agent.execute(ctx, "VERSION_DRIFT_CHECK")
        msgs = ctx.get_messages(msg_type=MessageType.INFORM)
        assert len(msgs) >= 1
        assert msgs[0].sender == "version_drift"
