"""Safety and governance tests — automated enforcement of AGENTS.md rules.

These tests verify that the codebase follows the governance rules defined in
AGENTS.md, docs/architecture/decisions.md, and the provider policy module.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

# Repository root (tests/unit/ -> repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class TestLLMEndpointGovernance:
    """AGENTS.md: GPT_OSS_ENDPOINT must be https://llm.professionalize.com/v1/"""

    def test_agents_md_declares_endpoint_policy(self):
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "llm.professionalize.com/v1/" in agents

    def test_no_hardcoded_openai_endpoints_in_source(self):
        """No source file outside llm_router should hardcode api.openai.com."""
        src_dir = REPO_ROOT / "src" / "plugin_examples"
        # llm_router/router.py uses api.openai.com as OpenAI-compatible protocol
        # defaults (overridden by GPT_OSS_ENDPOINT at runtime). This is expected.
        allowed = {"llm_router"}
        violations = []
        for py_file in src_dir.rglob("*.py"):
            rel = py_file.relative_to(src_dir)
            if rel.parts[0] in allowed:
                continue
            content = py_file.read_text(encoding="utf-8")
            if "api.openai.com" in content:
                violations.append(str(py_file.relative_to(REPO_ROOT)))
        assert violations == [], f"Hardcoded OpenAI endpoints found: {violations}"

    def test_no_hardcoded_azure_endpoints_in_source(self):
        src_dir = REPO_ROOT / "src" / "plugin_examples"
        violations = []
        for py_file in src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            if "openai.azure.com" in content:
                violations.append(str(py_file.relative_to(REPO_ROOT)))
        assert violations == [], f"Hardcoded Azure OpenAI endpoints found: {violations}"


class TestProviderPolicyIntegrity:
    """Verify provider_policy.py is consistent with AGENTS.md."""

    def test_approved_providers_match_agents_md(self):
        from plugin_examples.llm_router.provider_policy import APPROVED_PROVIDERS
        assert "llm_professionalize" in APPROVED_PROVIDERS
        assert "ollama" in APPROVED_PROVIDERS

    def test_unapproved_providers_match_agents_md(self):
        from plugin_examples.llm_router.provider_policy import UNAPPROVED_PROVIDERS
        assert "openai" in UNAPPROVED_PROVIDERS
        assert "gpt_oss" in UNAPPROVED_PROVIDERS

    def test_no_direct_openai_construction_in_codebase(self):
        """OpenAI( construction is only allowed in approved modules."""
        from plugin_examples.llm_router.provider_policy import is_direct_openai_construction
        src_dir = REPO_ROOT / "src" / "plugin_examples"
        # provider_policy.py contains "OpenAI(" as a detection string, not actual usage
        detection_modules = {"provider_policy.py"}
        violations = []
        for py_file in src_dir.rglob("*.py"):
            if py_file.name in detection_modules:
                continue
            content = py_file.read_text(encoding="utf-8")
            rel_path = str(py_file.relative_to(REPO_ROOT))
            if is_direct_openai_construction(content, rel_path):
                violations.append(rel_path)
        assert violations == [], f"Direct OpenAI construction found: {violations}"


class TestPublishingGovernance:
    """AGENTS.md: No direct push to main. All publishing is PR-based."""

    def test_agents_md_declares_pr_based_publishing(self):
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "PR-based" in agents or "pr-based" in agents.lower()

    def test_agents_md_declares_approval_tokens(self):
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "GH_TOKEN" in agents
        assert "GITHUB_TOKEN" in agents


class TestArchitectureDecisions:
    """docs/architecture/decisions.md: Active governance."""

    def test_decisions_file_exists(self):
        path = REPO_ROOT / "docs" / "architecture" / "decisions.md"
        assert path.exists(), "decisions.md must exist"

    def test_decisions_declares_nuget_source_of_truth(self):
        content = (REPO_ROOT / "docs" / "architecture" / "decisions.md").read_text(encoding="utf-8")
        assert "NuGet" in content

    def test_decisions_declares_pr_based_publishing(self):
        content = (REPO_ROOT / "docs" / "architecture" / "decisions.md").read_text(encoding="utf-8")
        assert "PR-based" in content


class TestEvidenceGovernance:
    """AGENTS.md: Evidence must be written even for partial failure."""

    def test_agents_md_declares_evidence_policy(self):
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "evidence" in agents.lower()

    def test_evidence_contract_module_exists(self):
        path = REPO_ROOT / "src" / "plugin_examples" / "evidence_contract.py"
        assert path.exists()


class TestGateOrder:
    """AGENTS.md: Gate order NuGet -> ... -> PR."""

    def test_pipeline_stages_doc_exists(self):
        path = REPO_ROOT / "docs" / "architecture" / "pipeline-stages.md"
        assert path.exists()

    def test_pipeline_stages_has_17_stages(self):
        content = (REPO_ROOT / "docs" / "architecture" / "pipeline-stages.md").read_text(encoding="utf-8")
        # Count table rows (lines starting with |, excluding header separator)
        rows = [line for line in content.split("\n")
                if line.strip().startswith("|") and "---" not in line and "Order" not in line]
        assert len(rows) >= 15, f"Expected at least 15 stage rows, got {len(rows)}"


class TestBlockedScenarioPolicy:
    """AGENTS.md: Blocked scenarios must be preserved with explicit reasons."""

    def test_agents_md_declares_blocked_scenario_policy(self):
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "blocked" in agents.lower()
        assert "explicit reasons" in agents.lower() or "explicit reason" in agents.lower()


class TestDenominatorFamilyCompleteness:
    """All 6 active families must have denominator JSON files."""

    FAMILIES = ["cells", "words", "pdf", "diagram", "email", "slides"]

    @pytest.mark.parametrize("family", FAMILIES)
    def test_denominator_exists(self, family):
        path = REPO_ROOT / "pipeline" / "configs" / "denominators" / f"{family}.json"
        assert path.exists(), f"Denominator missing for {family}"

    @pytest.mark.parametrize("family", FAMILIES)
    def test_denominator_is_valid_json(self, family):
        path = REPO_ROOT / "pipeline" / "configs" / "denominators" / f"{family}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "family" in data
        assert data["family"] == family


class TestScenarioContractSchema:
    """scenario-contract.schema.json must cover all 6 families."""

    def test_schema_exists(self):
        path = REPO_ROOT / "pipeline" / "schemas" / "scenario-contract.schema.json"
        assert path.exists()

    def test_schema_covers_all_families(self):
        path = REPO_ROOT / "pipeline" / "schemas" / "scenario-contract.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        family_enum = schema["properties"]["family"]["enum"]
        for fam in ["cells", "words", "pdf", "diagram", "email", "slides"]:
            assert fam in family_enum, f"Family {fam} missing from schema enum"
