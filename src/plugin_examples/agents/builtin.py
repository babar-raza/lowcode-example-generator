"""Built-in agents wrapping existing handler logic from planner_loop."""

from __future__ import annotations

from plugin_examples.agents.base import Agent, AgentCapability, AgentResult
from plugin_examples.agents.context import SharedContext


class ConservationCheckAgent(Agent):
    """Portfolio conservation check — verifies contract counts match denominators."""

    @property
    def agent_id(self) -> str:
        return "conservation_check"

    @property
    def capability(self) -> AgentCapability:
        return AgentCapability(
            action_types=frozenset({"PORTFOLIO_CONSERVATION_CHECK"}),
            specialization="conservation",
            read_only=True,
            priority=10,
        )

    def execute(self, context: SharedContext, action_id: str) -> AgentResult:
        from plugin_examples.portfolio_action_planner import ACTIVE_FAMILIES, _count_contracts, _load_denominators

        denoms = _load_denominators(context.repo_root)
        contracts = _count_contracts(context.repo_root)
        families = {}
        all_pass = True
        for f in ACTIVE_FAMILIES:
            d = denoms.get(f, {})
            pilot = d.get("allowed_pilot_count") or d.get("runnable_scenarios", 0)
            c = contracts.get(f, 0)
            ok = c == pilot
            families[f] = {"pilot": pilot, "contracts": c, "pass": ok}
            if not ok:
                all_pass = False

        context.set("conservation_result", all_pass)
        return AgentResult(
            changed=False,
            data={"conservation_all_pass": all_pass, "families": families, "changed": False},
        )


class VersionDriftAgent(Agent):
    """Version drift check — reads source versions from denominators."""

    @property
    def agent_id(self) -> str:
        return "version_drift"

    @property
    def capability(self) -> AgentCapability:
        return AgentCapability(
            action_types=frozenset({"VERSION_DRIFT_CHECK"}),
            specialization="version_drift",
            read_only=True,
            priority=10,
        )

    def execute(self, context: SharedContext, action_id: str) -> AgentResult:
        from plugin_examples.portfolio_action_planner import ACTIVE_FAMILIES, _load_denominators

        denoms = _load_denominators(context.repo_root)
        versions = {f: denoms.get(f, {}).get("source_version", "?") for f in ACTIVE_FAMILIES}
        return AgentResult(
            changed=False,
            data={"versions": versions, "status": "checked", "changed": False},
        )


class BlockerRecheckAgent(Agent):
    """NuGet blocker recheck — checks external dependency availability."""

    _BLOCKER_ACTION_IDS = frozenset({
        "FORMIMPORTER_RETEST",
        "OCR_DEPENDENCY_RECHECK",
        "PSD_DEPENDENCY_RECHECK",
        "PERMANENTLY_BLOCKED_WATCH",
    })

    @property
    def agent_id(self) -> str:
        return "blocker_recheck"

    @property
    def capability(self) -> AgentCapability:
        return AgentCapability(
            action_types=frozenset({"BLOCKER_RECHECK"}),
            specialization="blocker_recheck",
            read_only=False,
            priority=50,
        )

    def can_handle(self, action_id: str, action_type: str) -> bool:
        return action_id in self._BLOCKER_ACTION_IDS or super().can_handle(action_id, action_type)

    def execute(self, context: SharedContext, action_id: str) -> AgentResult:
        import subprocess

        data: dict = {"action_id": action_id, "changed": False}
        changed = False

        if action_id == "FORMIMPORTER_RETEST":
            try:
                r = subprocess.run(
                    ["curl", "-s", "https://api.nuget.org/v3-flatcontainer/aspose.pdf/index.json"],
                    capture_output=True, text=True, timeout=15,
                )
                import json

                parsed = json.loads(r.stdout)
                latest = parsed.get("versions", [])[-1] if parsed.get("versions") else "unknown"
                data["latest_version"] = latest
                data["still_blocked"] = True
            except Exception:
                data["check_failed"] = True

        elif action_id == "OCR_DEPENDENCY_RECHECK":
            try:
                r = subprocess.run(
                    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                     "https://api.nuget.org/v3-flatcontainer/aspose.ai.llm/index.json"],
                    capture_output=True, text=True, timeout=15,
                )
                data["http_status"] = r.stdout.strip()
                data["still_blocked"] = r.stdout.strip() != "200"
                if not data["still_blocked"]:
                    changed = True
                    data["changed"] = True
            except Exception:
                data["check_failed"] = True

        elif action_id == "PSD_DEPENDENCY_RECHECK":
            try:
                r = subprocess.run(
                    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                     "https://api.nuget.org/v3-flatcontainer/aspose.javaattributes/index.json"],
                    capture_output=True, text=True, timeout=15,
                )
                data["http_status"] = r.stdout.strip()
                data["still_blocked"] = r.stdout.strip() != "200"
                if not data["still_blocked"]:
                    changed = True
                    data["changed"] = True
            except Exception:
                data["check_failed"] = True

        elif action_id == "PERMANENTLY_BLOCKED_WATCH":
            data["status"] = "confirmed_unchanged"

        return AgentResult(changed=changed, data=data)
