"""
Plugin Identity Invariant Validators (14 rules: PIV-01..PIV-14)

Sprint: lowcode-plugin-canonical-identity-wave7-20260605

These validators prevent canonical identity defects from being silently
overlooked during dry-run example generation and publication classification.

A "generic/internal" name is one that does NOT match the canonical plugin slug
from products.aspose.net — e.g. "generate-barcode" vs "1d-barcode-writer".
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# Known internal/generic name patterns that must not appear as canonical slugs
GENERIC_BARCODE_SLUGS = {
    "generate-barcode",
    "recognize-barcode",
    "generate-qr-code",
    "scan-barcode",
    "read-barcode",
    "create-barcode",
}

# BarCode canonical plugin slugs
CANONICAL_BARCODE_SLUGS = {
    "1d-barcode-writer",
    "1d-barcode-reader",
    "2d-barcode-writer",
    "2d-barcode-reader",
}


@dataclass
class PivViolation:
    rule: str
    severity: str  # "ERROR" | "WARNING"
    message: str
    path: str = ""


@dataclass
class PivResult:
    package_key: str
    violations: List[PivViolation] = field(default_factory=list)
    identity_status: str = "UNKNOWN"

    @property
    def passes(self) -> bool:
        return not any(v.severity == "ERROR" for v in self.violations)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "WARNING")


def _read_json(path: Path) -> Optional[dict]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def run_plugin_identity_validators(pkg_dir: Path, package_key: str) -> PivResult:
    """
    Run all 14 plugin identity invariant rules on a single dry-run package.

    Args:
        pkg_dir: Path to the package directory.
        package_key: e.g. "barcode/1d-barcode-writer"

    Returns:
        PivResult with all violations.
    """
    result = PivResult(package_key=package_key)
    family, slug = package_key.split("/", 1) if "/" in package_key else ("", package_key)

    sp = _read_json(pkg_dir / "source-provenance.json") or {}
    ov = _read_json(pkg_dir / "output-validation.json") or {}
    pm = _read_json(pkg_dir / "package-manifest.json") or {}

    # PIV-01: source-provenance.json must exist
    if not (pkg_dir / "source-provenance.json").exists():
        result.violations.append(
            PivViolation(
                "PIV-01",
                "ERROR",
                "source-provenance.json missing — cannot verify canonical identity",
                str(pkg_dir / "source-provenance.json"),
            )
        )
    else:
        # PIV-02: canonical_url must be present and non-empty
        can_url = sp.get("canonical_url", "")
        if not can_url:
            result.violations.append(
                PivViolation(
                    "PIV-02",
                    "ERROR",
                    f"source-provenance.json missing canonical_url for {package_key}",
                    str(pkg_dir / "source-provenance.json"),
                )
            )

        # PIV-03: canonical_plugin_slug must be present
        can_slug = sp.get("canonical_plugin_slug", "")
        if not can_slug:
            result.violations.append(
                PivViolation(
                    "PIV-03",
                    "ERROR",
                    f"source-provenance.json missing canonical_plugin_slug for {package_key}",
                    str(pkg_dir / "source-provenance.json"),
                )
            )

        # PIV-04: canonical_url slug must match canonical_plugin_slug
        if can_url and can_slug:
            url_slug = can_url.rstrip("/").split("/")[-1]
            if url_slug and url_slug != can_slug:
                result.violations.append(
                    PivViolation(
                        "PIV-04",
                        "ERROR",
                        f"canonical_plugin_slug '{can_slug}' does not match slug in canonical_url '{url_slug}'",
                        str(pkg_dir / "source-provenance.json"),
                    )
                )

        # PIV-05: folder name must match canonical_plugin_slug (or be a documented alias)
        if can_slug and slug != can_slug:
            legacy = sp.get("legacy_example_slug", "")
            if slug == legacy or sp.get("identity_status") == "EXAMPLE_LEGACY_ALIAS_OK":
                result.violations.append(
                    PivViolation(
                        "PIV-05",
                        "WARNING",
                        f"Folder '{slug}' is a legacy alias for canonical slug '{can_slug}' — alias documented",
                        str(pkg_dir),
                    )
                )
            else:
                result.violations.append(
                    PivViolation(
                        "PIV-05",
                        "ERROR",
                        f"Folder '{slug}' does not match canonical_plugin_slug '{can_slug}' and no alias record",
                        str(pkg_dir),
                    )
                )

        # PIV-06: display_plugin_name must be present
        if not sp.get("display_plugin_name"):
            result.violations.append(
                PivViolation(
                    "PIV-06",
                    "WARNING",
                    f"source-provenance.json missing display_plugin_name for {package_key}",
                    str(pkg_dir / "source-provenance.json"),
                )
            )

        # PIV-07: identity_status must be present
        if not sp.get("identity_status"):
            result.violations.append(
                PivViolation(
                    "PIV-07",
                    "WARNING",
                    f"source-provenance.json missing identity_status for {package_key}",
                    str(pkg_dir / "source-provenance.json"),
                )
            )

    # PIV-08: BarCode generic names are never canonical
    if family == "barcode" and slug in GENERIC_BARCODE_SLUGS:
        result.violations.append(
            PivViolation(
                "PIV-08",
                "ERROR",
                f"BarCode folder '{slug}' uses internal generic name — must use one of {sorted(CANONICAL_BARCODE_SLUGS)}",
                str(pkg_dir),
            )
        )

    # PIV-09: README.md must exist
    readme_path = pkg_dir / "README.md"
    if not readme_path.exists():
        result.violations.append(
            PivViolation(
                "PIV-09",
                "WARNING",
                f"README.md missing for {package_key}",
                str(readme_path),
            )
        )
    else:
        readme_text = readme_path.read_text(encoding="utf-8", errors="replace")
        # PIV-10: README must not use only a generic internal operation name in the title
        first_line = readme_text.split("\n")[0].strip()
        for generic in GENERIC_BARCODE_SLUGS:
            if generic.replace("-", " ") in first_line.lower() and family == "barcode":
                result.violations.append(
                    PivViolation(
                        "PIV-10",
                        "WARNING",
                        f"README title '{first_line}' uses generic barcode name — use canonical display name",
                        str(readme_path),
                    )
                )

    # PIV-11: output-validation.json verdict must be present if exists
    if (pkg_dir / "output-validation.json").exists():
        verdict = ov.get("verdict", "")
        if not verdict:
            result.violations.append(
                PivViolation(
                    "PIV-11",
                    "WARNING",
                    f"output-validation.json missing verdict for {package_key}",
                    str(pkg_dir / "output-validation.json"),
                )
            )
        # PIV-12: PASS packages must have at least one non-zero output
        if verdict == "PASS":
            output_dir = pkg_dir / "output"
            if output_dir.exists():
                out_files = [f for f in output_dir.iterdir() if f.is_file() and f.stat().st_size > 0]
                if not out_files:
                    result.violations.append(
                        PivViolation(
                            "PIV-12",
                            "ERROR",
                            f"PASS verdict but no non-zero output files in output/ for {package_key}",
                            str(output_dir),
                        )
                    )

    # PIV-13: package-manifest.json must agree with source-provenance.json on canonical_url
    pm_url = pm.get("canonical_url", "")
    sp_url = sp.get("canonical_url", "")
    if pm_url and sp_url and pm_url != sp_url:
        result.violations.append(
            PivViolation(
                "PIV-13",
                "ERROR",
                f"package-manifest.json canonical_url '{pm_url}' differs from source-provenance.json '{sp_url}'",
                str(pkg_dir / "package-manifest.json"),
            )
        )

    # PIV-14: publication-local claim requires identity_status=CANONICAL_IDENTITY_VERIFIED
    pub_status = ov.get("publication_classification", "") or sp.get("publication_status", "")
    if "PUBLICATION_CANDIDATE_LOCAL_CLEAN" in pub_status:
        id_status = sp.get("identity_status", "")
        if id_status != "CANONICAL_IDENTITY_VERIFIED":
            result.violations.append(
                PivViolation(
                    "PIV-14",
                    "ERROR",
                    f"PUBLICATION_CANDIDATE_LOCAL_CLEAN claimed but identity_status='{id_status}' (need CANONICAL_IDENTITY_VERIFIED)",
                    str(pkg_dir / "source-provenance.json"),
                )
            )

    # Set overall identity_status
    if not result.violations:
        result.identity_status = "CANONICAL_IDENTITY_VERIFIED"
    elif result.passes:
        result.identity_status = "IDENTITY_WARNING_ONLY"
    else:
        result.identity_status = "IDENTITY_VIOLATION"

    return result


def run_all_plugin_identity_validators(
    examples_base: Path,
    alias_map: Optional[dict] = None,
) -> dict:
    """
    Run PIV validators on all packages in examples_base/{family}/{slug}/.

    Returns dict: package_key -> PivResult
    """
    results = {}
    if not examples_base.exists():
        return results
    for family_dir in sorted(examples_base.iterdir()):
        if not family_dir.is_dir():
            continue
        for pkg_dir in sorted(family_dir.iterdir()):
            if not pkg_dir.is_dir():
                continue
            key = f"{family_dir.name}/{pkg_dir.name}"
            r = run_plugin_identity_validators(pkg_dir, key)
            results[key] = r
    return results
