"""Tests for PluginDetection.fallback_strategy field — TC-IMPL-001."""

from __future__ import annotations

import copy
from pathlib import Path

import jsonschema
import pytest

from plugin_examples.family_config.models import PluginDetection
from plugin_examples.family_config.validator import validate_family_config
import plugin_examples.family_config.validator as _validator_module

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
LOWCODE_FAMILIES = ["cells", "words", "pdf", "slides", "email", "diagram"]
FAMILY_CONFIG_DIR = REPO_ROOT / "pipeline" / "configs" / "families"

# ---------------------------------------------------------------------------
# Minimal valid family config (does NOT need to be a real LowCode family)
# ---------------------------------------------------------------------------

_MINIMAL_CONFIG: dict = {
    "family": "test",
    "display_name": "Test Family",
    "enabled": True,
    "status": "active",
    "nuget": {
        "package_id": "Test.Package",
        "version_policy": "latest-stable",
    },
    "plugin_detection": {
        "namespace_patterns": ["Test.LowCode"],
    },
    "github": {
        "official_examples_repo": {"owner": "test", "repo": "test-repo", "branch": "main"},
        "published_plugin_examples_repo": {"owner": "test", "repo": "examples", "branch": "main"},
    },
    "fixtures": {"sources": []},
    "existing_examples": {"sources": []},
    "generation": {
        "min_examples_per_family": 1,
        "max_examples_per_monthly_run": 5,
    },
    "validation": {},
    "llm": {"provider_order": ["llm_professionalize"]},
}


@pytest.fixture(autouse=True)
def _clear_schema_cache():
    """Clear the schema cache before each test so the updated schema is loaded."""
    _validator_module._schema_cache = None
    yield
    _validator_module._schema_cache = None


# ---------------------------------------------------------------------------
# TC-IMPL-001 Tests
# ---------------------------------------------------------------------------


class TestFallbackStrategyDefaults:
    def test_fallback_strategy_defaults_to_none(self):
        """PluginDetection without fallback_strategy has fallback_strategy=None."""
        pd = PluginDetection(namespace_patterns=["Aspose.Cells.LowCode"])
        assert pd.fallback_strategy is None

    def test_fallback_strategy_capability_registry_accepted(self):
        """Schema accepts fallback_strategy='capability_registry'."""
        config = copy.deepcopy(_MINIMAL_CONFIG)
        config["plugin_detection"]["fallback_strategy"] = "capability_registry"
        # Should not raise
        validate_family_config(config)

    def test_fallback_strategy_invalid_value_raises_validation_error(self):
        """Schema rejects invalid fallback_strategy values."""
        config = copy.deepcopy(_MINIMAL_CONFIG)
        config["plugin_detection"]["fallback_strategy"] = "unsupported_value"
        with pytest.raises(jsonschema.ValidationError):
            validate_family_config(config)


class TestLowCodeYamlsUnaffected:
    """Existing LowCode family YAMLs must still load without error after the schema change."""

    @pytest.mark.parametrize("family", LOWCODE_FAMILIES)
    def test_lowcode_yaml_loads_without_error(self, family: str):
        """Load each LowCode family YAML and assert schema validation passes."""
        import yaml

        config_path = FAMILY_CONFIG_DIR / f"{family}.yml"
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        # Should not raise — fallback_strategy is optional
        validate_family_config(data)
