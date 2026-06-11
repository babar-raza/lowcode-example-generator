"""Shared downstream executor — Wave 23 Pipeline Parity.

Both LowCode and non-LowCode discovery paths produce PluginCandidate objects.
This module provides SharedDownstreamExecutor which runs all post-discovery
pipeline steps identically for both sources.

Discovery divergence (the ONLY allowed difference):
  - LowCode:        namespace scan -> candidates
  - Non-LowCode:    capability registry lookup -> candidates

Everything downstream of discovery is handled here:
  - Artifact contract validation (manifest, expected output, README)
  - PR packet assembly
  - Publication state tracking
  - Evidence capture
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class PluginCandidate:
    """Minimal candidate record produced by either discovery path."""

    slug: str
    family: str
    namespace_source: str  # "LOWCODE" | "NON_LOWCODE_PLUGIN"
    discovery_method: str  # "namespace_scan" | "capability_registry_fallback" | "manual"
    example_dir: Path | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class DownstreamResult:
    """Result of running a single candidate through the shared downstream."""

    slug: str
    family: str
    namespace_source: str
    discovery_method: str
    artifact_contract: dict = field(default_factory=dict)
    pr_packet: dict = field(default_factory=dict)
    publication_state: str = "PENDING"
    evidence: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


@dataclass
class BatchResult:
    """Aggregated results for a batch of candidates."""

    candidates: int = 0
    passed: int = 0
    failed: int = 0
    results: list[DownstreamResult] = field(default_factory=list)

    def add(self, r: DownstreamResult) -> None:
        self.candidates += 1
        self.results.append(r)
        if r.ok:
            self.passed += 1
        else:
            self.failed += 1


# ---------------------------------------------------------------------------
# Artifact contract checkers (identical for both sources)
# ---------------------------------------------------------------------------


def _check_manifest(example_dir: Path, result: DownstreamResult) -> None:
    manifest = example_dir / "example.manifest.json"
    if manifest.exists():
        result.artifact_contract["manifest"] = "PRESENT"
        result.evidence.append(str(manifest))
    else:
        result.artifact_contract["manifest"] = "MISSING"
        result.errors.append(f"example.manifest.json missing in {example_dir}")


def _check_expected_output(example_dir: Path, result: DownstreamResult) -> None:
    eo = example_dir / "expected-output.json"
    if eo.exists():
        result.artifact_contract["expected_output"] = "PRESENT"
        result.evidence.append(str(eo))
    else:
        result.artifact_contract["expected_output"] = "MISSING"
        result.errors.append(f"expected-output.json missing in {example_dir}")


def _check_readme(example_dir: Path, result: DownstreamResult) -> None:
    readme = example_dir / "README.md"
    if readme.exists():
        content = readme.read_text(encoding="utf-8", errors="replace")
        sections = []
        for heading in ("## Purpose", "## Prerequisites", "## Expected Output"):
            if heading in content:
                sections.append(heading)
        quality = "QUALITY" if len(sections) >= 3 else "MINIMAL"
        result.artifact_contract["readme"] = quality
        result.artifact_contract["readme_sections"] = sections
        result.evidence.append(str(readme))
        if quality == "MINIMAL":
            result.errors.append(
                f"README.md is MINIMAL (missing sections: "
                f"{[h for h in ('## Purpose','## Prerequisites','## Expected Output') if h not in sections]})"
            )
    else:
        result.artifact_contract["readme"] = "MISSING"
        result.errors.append(f"README.md missing in {example_dir}")


def _check_pr_packet(candidate: PluginCandidate, result: DownstreamResult) -> None:
    """Assemble canonical PR packet fields — identical structure for both sources."""
    result.pr_packet = {
        "slug": candidate.slug,
        "family": candidate.family,
        "namespace_source": candidate.namespace_source,
        "discovery_method": candidate.discovery_method,
        "pr_title_prefix": (
            "feat(plugins):" if candidate.namespace_source == "NON_LOWCODE_PLUGIN" else "feat(lowcode):"
        ),
        "branch_prefix": ("plugins" if candidate.namespace_source == "NON_LOWCODE_PLUGIN" else "lowcode-examples"),
    }


# ---------------------------------------------------------------------------
# SharedDownstreamExecutor
# ---------------------------------------------------------------------------


class SharedDownstreamExecutor:
    """Runs all post-discovery pipeline steps for any PluginCandidate.

    The execute() method is the single entry point — it is called with
    the same arguments regardless of whether the candidate came from the
    LowCode namespace scan or the non-LowCode capability registry lookup.

    This fulfils the Wave 23 Lane C requirement: only candidate *discovery*
    may differ between the two pipelines; everything downstream is shared.
    """

    def __init__(self, strict: bool = True) -> None:
        self.strict = strict

    def execute(self, candidate: PluginCandidate) -> DownstreamResult:
        """Process a single candidate through all downstream steps."""
        result = DownstreamResult(
            slug=candidate.slug,
            family=candidate.family,
            namespace_source=candidate.namespace_source,
            discovery_method=candidate.discovery_method,
        )

        # Step 1: artifact contract (same for both sources)
        if candidate.example_dir is not None:
            _check_manifest(candidate.example_dir, result)
            _check_expected_output(candidate.example_dir, result)
            _check_readme(candidate.example_dir, result)
        else:
            result.artifact_contract["example_dir"] = "NOT_PROVIDED"
            # No dir provided is only allowed in non-strict mode
            if self.strict:
                result.errors.append("example_dir not provided — required in strict mode")

        # Step 2: PR packet assembly (same structure for both sources)
        _check_pr_packet(candidate, result)

        # Step 3: publication state
        if result.ok:
            result.publication_state = "READY_FOR_PR"
        else:
            result.publication_state = "NEEDS_REPAIR"

        return result

    def execute_batch(self, candidates: list[PluginCandidate]) -> BatchResult:
        """Process multiple candidates, accumulating results."""
        batch = BatchResult()
        for candidate in candidates:
            batch.add(self.execute(candidate))
        return batch


# ---------------------------------------------------------------------------
# Discovery adapters (the ONLY divergent part)
# ---------------------------------------------------------------------------


def discover_lowcode_candidates(
    namespace_patterns: list[str],
    family: str,
    example_dirs: list[Path],
) -> list[PluginCandidate]:
    """LowCode discovery: namespace scan -> candidates.

    In production this uses the namespace scanner; here we accept pre-resolved
    example_dirs to keep the adapter thin and testable.
    """
    candidates = []
    for d in example_dirs:
        slug = d.name
        matched = any(slug.startswith(p) or p in slug for p in namespace_patterns)
        if matched or not namespace_patterns:
            candidates.append(
                PluginCandidate(
                    slug=slug,
                    family=family,
                    namespace_source="LOWCODE",
                    discovery_method="namespace_scan",
                    example_dir=d,
                )
            )
    return candidates


def discover_nonlowcode_candidates(
    registry_entries: list[dict[str, Any]],
    family: str,
    example_dirs: list[Path],
) -> list[PluginCandidate]:
    """Non-LowCode discovery: capability registry lookup -> candidates.

    In production this reads the plugin capability registry; here we accept
    pre-resolved registry_entries + example_dirs.
    """
    dir_map = {d.name: d for d in example_dirs}
    candidates = []
    for entry in registry_entries:
        slug = entry.get("slug", "")
        candidates.append(
            PluginCandidate(
                slug=slug,
                family=family,
                namespace_source="NON_LOWCODE_PLUGIN",
                discovery_method="capability_registry_fallback",
                example_dir=dir_map.get(slug),
                metadata=entry,
            )
        )
    return candidates
