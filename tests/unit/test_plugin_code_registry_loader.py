"""Unit tests for plugin-code registry loader."""
import pytest
from pathlib import Path
from src.plugin_examples.plugin_code_registry.loader import PluginCodeRegistryLoader
from src.plugin_examples.plugin_code_registry.models import PluginEntry, FamilyRegistry


@pytest.fixture
def loader():
    return PluginCodeRegistryLoader().load()


def test_loader_loads_families(loader):
    families = loader.all_families()
    assert len(families) >= 10, "Expected at least 10 family registries"


def test_loader_excludes_protected_families(loader):
    non_protected = loader.non_protected_families()
    protected = {"cells", "words", "pdf", "slides", "email", "diagram"}
    assert not any(f in non_protected for f in protected), "Protected families must not appear in non_protected_families()"


def test_ready_entries_non_empty(loader):
    # active_entries includes READY + TRANSFORMED + PUBLICATION_CANDIDATE (pipeline total)
    active = loader.active_entries()
    assert len(active) >= 25, f"Expected at least 25 active pipeline entries, got {len(active)}"


def test_ready_entries_sorted_by_score(loader):
    ready = loader.ready_entries()
    scores = [e.readiness_score() for e in ready]
    assert scores == sorted(scores, reverse=True), "ready_entries must be sorted by descending score"


def test_all_ready_entries_have_canonical_url(loader):
    violations = []
    for entry in loader.ready_entries():
        if not entry.canonical_url:
            violations.append(f"{entry.family}/{entry.plugin_slug}")
    assert not violations, f"READY entries missing canonical_url: {violations}"


def test_validate_entry_returns_violations_for_bad_entry():
    loader = PluginCodeRegistryLoader()
    bad = PluginEntry(
        family="test",
        plugin_slug="bad-entry",
        registry_status="READY_FOR_TRANSFORMATION",
    )
    violations = loader.validate_entry(bad)
    assert len(violations) >= 3, f"Expected violations for incomplete entry, got: {violations}"


def test_validate_entry_passes_for_good_entry():
    loader = PluginCodeRegistryLoader()
    good = PluginEntry(
        family="barcode",
        plugin_slug="generate-barcode",
        registry_status="READY_FOR_TRANSFORMATION",
        canonical_url="https://products.aspose.net/barcode/1d-barcode-writer/",
        page_source_status="CANONICAL_URL_CONFIRMED",
        implementation_model="STATIC_CONVERTER_CLASS",
        classes_used=["BarcodeGenerator", "EncodeTypes"],
        transformation_readiness_reason="Canonical URL confirmed, code harvested",
    )
    violations = loader.validate_entry(good)
    assert not violations, f"Expected no violations for complete entry, got: {violations}"


def test_select_wave_respects_exclusion(loader):
    exclude = {"barcode/generate-barcode", "imaging/convert-image"}
    wave = loader.select_wave(exclude_slugs=exclude, limit=10)
    slugs = {f"{e.family}/{e.plugin_slug}" for e in wave}
    assert not (slugs & exclude), "Excluded slugs must not appear in wave selection"


def test_select_wave_respects_limit(loader):
    wave = loader.select_wave(limit=5)
    assert len(wave) <= 5


def test_build_readiness_matrix(loader):
    matrix = loader.build_readiness_matrix()
    assert "families" in matrix
    assert "status_counts" in matrix
    assert "violations" in matrix
    assert "barcode" in matrix["families"]
    assert not matrix["violations"], f"Expected 0 violations after Sprint repairs, got: {matrix['violations']}"


def test_family_registry_ready_plugins(loader):
    barcode = loader.all_families().get("barcode")
    assert barcode is not None
    # Count READY + TRANSFORMED + CANONICAL_PACKAGE_PROVEN (W18 advanced 1d/2d readers to PROVEN)
    active = [p for p in barcode.plugins if p.registry_status in (
        "READY_FOR_TRANSFORMATION", "TRANSFORMED_TO_EXAMPLE_DRYRUN", "CANONICAL_PACKAGE_PROVEN")]
    assert len(active) >= 4, "barcode should have at least 4 active entries (READY/TRANSFORMED/PROVEN)"


def test_plugin_entry_is_fixture_free_for_barcode():
    entry = PluginEntry(
        family="barcode", plugin_slug="generate-qr-code",
        registry_status="READY_FOR_TRANSFORMATION",
        implementation_model="STATIC_CONVERTER_CLASS",
    )
    assert entry.is_fixture_free


def test_plugin_entry_readiness_score_increases_with_evidence():
    low = PluginEntry(family="test", plugin_slug="x", registry_status="CODE_HARVESTED")
    high = PluginEntry(
        family="barcode", plugin_slug="y",
        registry_status="READY_FOR_TRANSFORMATION",
        canonical_url="https://example.com",
        implementation_model="STATIC_CONVERTER_CLASS",
        code_hashes=["abc"],
    )
    assert high.readiness_score() > low.readiness_score()
