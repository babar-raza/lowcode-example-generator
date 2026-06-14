"""Tests for built-in agents — ConservationCheck, VersionDrift, BlockerRecheck."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.agents.builtin import BlockerRecheckAgent, ConservationCheckAgent, VersionDriftAgent
from plugin_examples.agents.context import SharedContext


def _ctx(tmp_path: Path) -> SharedContext:
    ev = tmp_path / "evidence"
    ev.mkdir(exist_ok=True)
    return SharedContext(repo_root=tmp_path, evidence_dir=ev)


class TestConservationCheckAgent:
    def test_agent_id(self):
        assert ConservationCheckAgent().agent_id == "conservation_check"

    def test_capability(self):
        cap = ConservationCheckAgent().capability
        assert "PORTFOLIO_CONSERVATION_CHECK" in cap.action_types
        assert cap.read_only is True
        assert cap.specialization == "conservation"

    def test_can_handle(self):
        agent = ConservationCheckAgent()
        assert agent.can_handle("any", "PORTFOLIO_CONSERVATION_CHECK")
        assert not agent.can_handle("any", "OTHER_TYPE")

    @patch("plugin_examples.portfolio_action_planner.ACTIVE_FAMILIES", ["cells"])
    @patch("plugin_examples.portfolio_action_planner._count_contracts", return_value={"cells": 5})
    @patch("plugin_examples.portfolio_action_planner._load_denominators", return_value={"cells": {"allowed_pilot_count": 5}})
    def test_execute_all_pass(self, mock_denoms, mock_contracts, tmp_path: Path):
        agent = ConservationCheckAgent()
        ctx = _ctx(tmp_path)
        result = agent.execute(ctx, "PORTFOLIO_CONSERVATION_CHECK")
        assert result.changed is False
        assert result.data["conservation_all_pass"] is True
        assert ctx.get("conservation_result") is True

    @patch("plugin_examples.portfolio_action_planner.ACTIVE_FAMILIES", ["cells"])
    @patch("plugin_examples.portfolio_action_planner._count_contracts", return_value={"cells": 3})
    @patch("plugin_examples.portfolio_action_planner._load_denominators", return_value={"cells": {"allowed_pilot_count": 5}})
    def test_execute_mismatch(self, mock_denoms, mock_contracts, tmp_path: Path):
        agent = ConservationCheckAgent()
        ctx = _ctx(tmp_path)
        result = agent.execute(ctx, "PORTFOLIO_CONSERVATION_CHECK")
        assert result.data["conservation_all_pass"] is False
        assert ctx.get("conservation_result") is False


class TestVersionDriftAgent:
    def test_agent_id(self):
        assert VersionDriftAgent().agent_id == "version_drift"

    def test_capability(self):
        cap = VersionDriftAgent().capability
        assert "VERSION_DRIFT_CHECK" in cap.action_types
        assert cap.read_only is True

    @patch("plugin_examples.portfolio_action_planner.ACTIVE_FAMILIES", ["pdf"])
    @patch("plugin_examples.portfolio_action_planner._load_denominators", return_value={"pdf": {"source_version": "25.5.0"}})
    def test_execute(self, mock_denoms, tmp_path: Path):
        agent = VersionDriftAgent()
        result = agent.execute(_ctx(tmp_path), "VERSION_DRIFT_CHECK")
        assert result.changed is False
        assert result.data["versions"]["pdf"] == "25.5.0"


class TestBlockerRecheckAgent:
    def test_agent_id(self):
        assert BlockerRecheckAgent().agent_id == "blocker_recheck"

    def test_can_handle_by_action_id(self):
        agent = BlockerRecheckAgent()
        assert agent.can_handle("FORMIMPORTER_RETEST", "ANY")
        assert agent.can_handle("OCR_DEPENDENCY_RECHECK", "ANY")
        assert agent.can_handle("PSD_DEPENDENCY_RECHECK", "ANY")
        assert agent.can_handle("PERMANENTLY_BLOCKED_WATCH", "ANY")

    def test_can_handle_by_type(self):
        agent = BlockerRecheckAgent()
        assert agent.can_handle("unknown_id", "BLOCKER_RECHECK")

    def test_cannot_handle_unknown(self):
        agent = BlockerRecheckAgent()
        assert not agent.can_handle("unknown_id", "UNKNOWN_TYPE")

    def test_permanently_blocked(self, tmp_path: Path):
        agent = BlockerRecheckAgent()
        result = agent.execute(_ctx(tmp_path), "PERMANENTLY_BLOCKED_WATCH")
        assert result.changed is False
        assert result.data["status"] == "confirmed_unchanged"

    @patch("subprocess.run")
    def test_formimporter_retest(self, mock_run, tmp_path: Path):
        mock_run.return_value = MagicMock(stdout='{"versions": ["25.4.0", "25.5.0"]}')
        agent = BlockerRecheckAgent()
        result = agent.execute(_ctx(tmp_path), "FORMIMPORTER_RETEST")
        assert result.changed is False
        assert result.data["latest_version"] == "25.5.0"
        assert result.data["still_blocked"] is True
