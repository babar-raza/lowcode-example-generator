"""Probe executor: orchestrate probe generation, execution, and classification.

Takes registry entries, generates family-aware probe code, runs dotnet
restore/build/run via ProbeRunner, and returns classified ProbeOutcome objects.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from plugin_examples.probe_generator.registry_probe import (
    generate_probe_from_registry,
)
from plugin_examples.probe_generator.runner import ProbeResult, ProbeRunner

logger = logging.getLogger(__name__)

_PROBEABLE_STATUSES = frozenset({
    "REFLECTION_CANDIDATE",
    "WEBSITE_DISCOVERED",
    "PROBE_CANDIDATE",
})


@dataclass
class ProbeOutcome:
    """Result of probing a single registry entry."""

    family: str
    plugin_slug: str
    new_status: str  # PROBE_CONFIRMED or PROBE_FAILED_*
    probe_result: ProbeResult | None
    probe_evidence_path: str
    entry: dict
    duration_ms: int = 0
    error: str | None = None


class ProbeExecutor:
    """Probe registry entries by generating and running C# probe code.

    Args:
        repo_root: Repository root path.
        timeout: Per-phase subprocess timeout in seconds (restore, build, run).
    """

    def __init__(self, repo_root: Path, timeout: int = 120):
        self.repo_root = Path(repo_root)
        self.timeout = timeout
        self._probes_dir = self.repo_root / ".local" / "psal" / "probes"
        self._check_dotnet()

    def _check_dotnet(self) -> None:
        """Verify dotnet SDK is available."""
        try:
            result = subprocess.run(
                ["dotnet", "--version"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode != 0:
                raise RuntimeError(f"dotnet --version failed: {result.stderr}")
            logger.info("dotnet SDK: %s", result.stdout.strip())
        except FileNotFoundError:
            raise RuntimeError(
                "dotnet SDK not found. Install .NET SDK 8.0+ to run probes."
            ) from None

    def probe_entry(self, family: str, entry: dict) -> ProbeOutcome:
        """Probe a single registry entry.

        Generates C# probe code, runs dotnet restore/build/run, classifies result.

        Args:
            family: Family slug.
            entry: Registry entry dict from YAML.

        Returns:
            ProbeOutcome with classification and evidence path.
        """
        slug = entry.get("plugin_slug", "unknown")
        probe_dir = self._probes_dir / family / slug
        if probe_dir.exists():
            shutil.rmtree(probe_dir)

        t0 = time.monotonic()
        try:
            probe_files = generate_probe_from_registry(entry, probe_dir)
        except Exception as exc:
            return ProbeOutcome(
                family=family,
                plugin_slug=slug,
                new_status="PROBE_FAILED_BUILD",
                probe_result=None,
                probe_evidence_path=str(probe_dir),
                entry=entry,
                duration_ms=int((time.monotonic() - t0) * 1000),
                error=f"Code generation failed: {exc}",
            )

        runner = ProbeRunner(timeout=self.timeout)
        try:
            result = runner.run(probe_dir, probe_files.csproj_path, log_dir=probe_dir)
        except Exception as exc:
            return ProbeOutcome(
                family=family,
                plugin_slug=slug,
                new_status="PROBE_FAILED_BUILD",
                probe_result=None,
                probe_evidence_path=str(probe_dir),
                entry=entry,
                duration_ms=int((time.monotonic() - t0) * 1000),
                error=f"Probe runner crashed: {exc}",
            )

        duration = int((time.monotonic() - t0) * 1000)

        new_status = "PROBE_CONFIRMED" if result.failure_taxonomy is None else result.failure_taxonomy

        evidence_path = str(probe_dir / "probe-outcome.json")
        outcome = ProbeOutcome(
            family=family,
            plugin_slug=slug,
            new_status=new_status,
            probe_result=result,
            probe_evidence_path=evidence_path,
            entry=entry,
            duration_ms=duration,
        )

        self._write_evidence(outcome)
        return outcome

    def probe_family(self, family: str, registry_path: Path | None = None) -> list[ProbeOutcome]:
        """Probe all eligible entries for a family.

        Args:
            family: Family slug.
            registry_path: Optional explicit path to registry YAML.
                Defaults to ``pipeline/plugin-capability-registry/{family}.yaml``.

        Returns:
            List of ProbeOutcome for each probed entry.
        """
        if registry_path is None:
            registry_path = self.repo_root / "pipeline" / "plugin-capability-registry" / f"{family}.yaml"

        if not registry_path.exists():
            logger.warning("No registry file at %s", registry_path)
            return []

        entries = _load_registry_entries(registry_path)
        eligible = [e for e in entries if e.get("status") in _PROBEABLE_STATUSES]

        if not eligible:
            logger.info("No probeable entries for %s (statuses: %s)",
                        family, [e.get("status") for e in entries])
            return []

        outcomes: list[ProbeOutcome] = []
        for entry in eligible:
            slug = entry.get("plugin_slug", "unknown")
            logger.info("Probing %s/%s ...", family, slug)
            try:
                outcome = self.probe_entry(family, entry)
            except Exception as exc:
                logger.error("Probe crashed for %s/%s: %s", family, slug, exc)
                outcome = ProbeOutcome(
                    family=family,
                    plugin_slug=slug,
                    new_status="PROBE_FAILED_BUILD",
                    probe_result=None,
                    probe_evidence_path="",
                    entry=entry,
                    error=str(exc),
                )
            outcomes.append(outcome)
            logger.info("  -> %s (%dms)", outcome.new_status, outcome.duration_ms)

        return outcomes

    def _write_evidence(self, outcome: ProbeOutcome) -> None:
        """Write probe outcome to JSON for evidence trail."""
        evidence = {
            "family": outcome.family,
            "plugin_slug": outcome.plugin_slug,
            "new_status": outcome.new_status,
            "duration_ms": outcome.duration_ms,
            "error": outcome.error,
        }
        if outcome.probe_result is not None:
            evidence["probe_result"] = {
                "restore_ok": outcome.probe_result.restore_ok,
                "build_ok": outcome.probe_result.build_ok,
                "run_ok": outcome.probe_result.run_ok,
                "output_validated": outcome.probe_result.output_validated,
                "output_size_bytes": outcome.probe_result.output_size_bytes,
                "failure_taxonomy": outcome.probe_result.failure_taxonomy,
                "failure_detail": outcome.probe_result.failure_detail,
                "exit_codes": outcome.probe_result.exit_codes,
            }

        path = Path(outcome.probe_evidence_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")


def _load_registry_entries(registry_path: Path) -> list[dict]:
    """Load entries from a capability registry YAML file."""
    import yaml

    text = registry_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    return data.get("entries", [])
