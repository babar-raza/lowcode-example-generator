"""Non-LowCode Pipeline Parity Validators (PPV-01..16).

These validators would have caught every non-LowCode pipeline flaw before PR creation.
All checks are offline (no network), deterministic, and additive.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PpvResult:
    checks: list[dict] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    warnings: int = 0

    def ok(self, code: str, msg: str) -> None:
        self.checks.append({"code": code, "status": "PASS", "message": msg})
        self.passed += 1

    def fail(self, code: str, msg: str, path: str = "") -> None:
        self.checks.append({"code": code, "status": "FAIL", "message": msg, "path": path})
        self.failed += 1

    def warn(self, code: str, msg: str) -> None:
        self.checks.append({"code": code, "status": "WARN", "message": msg})
        self.warnings += 1


def _is_lowcode_family(manifest: dict) -> bool:
    """Return True if manifest/closeout describes a LowCode-namespace family."""
    return manifest.get("namespace_source", "LOWCODE") == "LOWCODE"


# ─── PPV-01: PR title must not use 'feat(lowcode)' for non-LowCode repos ──────
def check_ppv_01_pr_title_no_lowcode(pr_packet: dict, result: PpvResult) -> None:
    """PR title must not say feat(lowcode) for NON_LOWCODE_PLUGIN families."""
    ns = pr_packet.get("namespace_source", "LOWCODE")
    title = pr_packet.get("pr_title", "")
    if ns == "NON_LOWCODE_PLUGIN" and re.search(r"feat\s*\(\s*lowcode\s*\)", title, re.IGNORECASE):
        result.fail("PPV-01", f"PR title uses 'feat(lowcode)' for NON_LOWCODE_PLUGIN family: {title!r}")
    else:
        result.ok("PPV-01", "PR title terminology correct for namespace_source")


# ─── PPV-02: PR body must not say 'low-code' for non-LowCode repos ───────────
def check_ppv_02_pr_body_no_lowcode(pr_packet: dict, result: PpvResult) -> None:
    ns = pr_packet.get("namespace_source", "LOWCODE")
    body = pr_packet.get("pr_body", "")
    if ns == "NON_LOWCODE_PLUGIN" and re.search(r"low.?code", body, re.IGNORECASE):
        result.fail("PPV-02", "PR body uses 'low-code' or 'lowcode' wording for NON_LOWCODE_PLUGIN family")
    else:
        result.ok("PPV-02", "PR body terminology correct for namespace_source")


# ─── PPV-03: Branch naming convention warn for 'lowcode/' on non-LowCode ─────
def check_ppv_03_branch_naming_warn(pr_packet: dict, result: PpvResult) -> None:
    ns = pr_packet.get("namespace_source", "LOWCODE")
    branch = pr_packet.get("branch_name", "")
    if ns == "NON_LOWCODE_PLUGIN" and branch.startswith("lowcode/"):
        result.warn(
            "PPV-03",
            f"Branch '{branch}' uses 'lowcode/' prefix for NON_LOWCODE_PLUGIN family (legacy; use 'plugins/' for new branches)",
        )
    else:
        result.ok("PPV-03", "Branch naming acceptable")


# ─── PPV-04: example.manifest.json must exist ────────────────────────────────
def check_ppv_04_manifest_exists(example_dir: Path, result: PpvResult) -> None:
    p = example_dir / "example.manifest.json"
    if not p.exists():
        result.fail("PPV-04", "Missing example.manifest.json", str(p))
    else:
        result.ok("PPV-04", f"example.manifest.json present: {p}")


# ─── PPV-05: expected-output.json must exist ─────────────────────────────────
def check_ppv_05_expected_output_exists(example_dir: Path, result: PpvResult) -> None:
    p = example_dir / "expected-output.json"
    if not p.exists():
        result.fail("PPV-05", "Missing expected-output.json", str(p))
    else:
        result.ok("PPV-05", f"expected-output.json present: {p}")


# ─── PPV-06: output-validation.json must not substitute expected-output.json ─
def check_ppv_06_output_validation_not_only_contract(example_dir: Path, result: PpvResult) -> None:
    ov = example_dir / "output-validation.json"
    eo = example_dir / "expected-output.json"
    if ov.exists() and not eo.exists():
        result.fail(
            "PPV-06",
            "output-validation.json exists but expected-output.json is missing; internal evidence must not replace public contract",
            str(example_dir),
        )
    else:
        result.ok("PPV-06", "output-validation.json does not substitute expected-output.json")


# ─── PPV-07: Directory.Packages.props must exist at repo root ────────────────
def check_ppv_07_dir_packages_props(repo_root: Path, result: PpvResult) -> None:
    p = repo_root / "Directory.Packages.props"
    if not p.exists():
        result.fail("PPV-07", "Missing Directory.Packages.props (central package management required)", str(p))
    else:
        result.ok("PPV-07", "Directory.Packages.props present")


# ─── PPV-08: csproj must not have explicit Version in PackageReference ────────
def check_ppv_08_csproj_no_version(csproj_path: Path, result: PpvResult) -> None:
    if not csproj_path.exists():
        result.fail("PPV-08", f"csproj not found: {csproj_path}")
        return
    content = csproj_path.read_text(encoding="utf-8")
    if re.search(r"<PackageReference\s[^>]*Version=", content):
        result.fail(
            "PPV-08",
            f"csproj has explicit Version in PackageReference (use central management): {csproj_path.name}",
            str(csproj_path),
        )
    else:
        result.ok("PPV-08", f"csproj uses central package management: {csproj_path.name}")


# ─── PPV-09: Root README.md must exist ───────────────────────────────────────
def check_ppv_09_root_readme(repo_root: Path, result: PpvResult) -> None:
    p = repo_root / "README.md"
    if not p.exists():
        result.fail("PPV-09", "Missing root README.md", str(p))
    else:
        result.ok("PPV-09", "Root README.md present")


# ─── PPV-10: CI workflow must exist ─────────────────────────────────────────
def check_ppv_10_ci_workflow(repo_root: Path, result: PpvResult) -> None:
    wf_dir = repo_root / ".github" / "workflows"
    if not wf_dir.exists() or not any(wf_dir.glob("*.yml")):
        result.fail("PPV-10", "Missing .github/workflows/*.yml CI workflow", str(wf_dir))
    else:
        result.ok("PPV-10", f"CI workflow present: {list(wf_dir.glob('*.yml'))[0].name}")


# ─── PPV-11: Folder layout must match approved convention ────────────────────
def check_ppv_11_folder_layout(
    example_dir: Path, family: str, slug: str, namespace_source: str, result: PpvResult
) -> None:
    """
    LOWCODE: must be examples/<family>/lowcode/<slug>
    NON_LOWCODE_PLUGIN in plugin-only repo: must be examples/<family>/<slug>
    """
    parts = example_dir.parts
    if namespace_source == "LOWCODE":
        expected = ("examples", family, "lowcode", slug)
        ok = len(parts) >= 4 and parts[-4:] == expected
        if not ok:
            result.fail("PPV-11", f"LowCode example must be at examples/{family}/lowcode/{slug}/, found: {example_dir}")
        else:
            result.ok("PPV-11", f"Folder layout correct: examples/{family}/lowcode/{slug}/")
    else:
        expected = ("examples", family, slug)
        ok = len(parts) >= 3 and parts[-3:] == expected
        if not ok:
            result.fail("PPV-11", f"Non-LowCode example must be at examples/{family}/{slug}/, found: {example_dir}")
        else:
            result.ok("PPV-11", f"Folder layout correct: examples/{family}/{slug}/")


# ─── PPV-12: Binary fixture must have provenance documented in manifest ───────
def check_ppv_12_fixture_provenance(example_dir: Path, result: PpvResult) -> None:
    manifest_path = example_dir / "example.manifest.json"
    if not manifest_path.exists():
        result.ok("PPV-12", "Skipped (no manifest to check provenance against)")
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        result.warn("PPV-12", f"Could not parse manifest for provenance check: {manifest_path}")
        return
    input_files = manifest.get("input_files", [])
    for fname in input_files:
        fixture = example_dir / fname
        if fixture.exists() and fixture.stat().st_size > 0:
            # Provenance considered documented if manifest has input_strategy and canonical_url
            has_strategy = bool(manifest.get("input_strategy"))
            has_url = bool(manifest.get("canonical_url"))
            if not (has_strategy and has_url):
                result.warn(
                    "PPV-12",
                    f"Fixture {fname} exists but provenance (input_strategy/canonical_url) incomplete in manifest",
                )
            else:
                result.ok("PPV-12", f"Fixture provenance documented: {fname} via {manifest.get('input_strategy')}")
        else:
            result.ok("PPV-12", f"No binary fixture found for {fname} or fixture is inline")


# ─── PPV-13: manifest namespace_source must match family config ───────────────
def check_ppv_13_manifest_namespace_source(example_dir: Path, expected_ns: str, result: PpvResult) -> None:
    manifest_path = example_dir / "example.manifest.json"
    if not manifest_path.exists():
        result.ok("PPV-13", "Skipped (no manifest)")
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        result.warn("PPV-13", "Could not parse manifest")
        return
    actual_ns = manifest.get("namespace_source", "LOWCODE")
    if actual_ns != expected_ns:
        result.fail("PPV-13", f"Manifest namespace_source={actual_ns!r} does not match expected={expected_ns!r}")
    else:
        result.ok("PPV-13", f"Manifest namespace_source={actual_ns!r} matches config")


# ─── PPV-14: Status must not be inflated (PCLC ≠ PR_READY ≠ PR_CREATED) ──────
def check_ppv_14_status_not_inflated(registry_entry: dict, result: PpvResult) -> None:
    status = registry_entry.get("registry_status", "")
    pr_url = registry_entry.get("pr_url", "")
    # PR_CREATED requires a real URL
    if status == "PR_CREATED" and not pr_url:
        result.fail("PPV-14", f"registry_status=PR_CREATED but no pr_url: {registry_entry.get('slug','?')}")
    elif status == "PUBLISHED" and not registry_entry.get("published_at"):
        result.fail("PPV-14", f"registry_status=PUBLISHED but no published_at: {registry_entry.get('slug','?')}")
    else:
        result.ok("PPV-14", f"Status not inflated: {status}")


# ─── PPV-15: .gitignore must exist ───────────────────────────────────────────
def check_ppv_15_gitignore(repo_root: Path, result: PpvResult) -> None:
    p = repo_root / ".gitignore"
    if not p.exists():
        result.fail("PPV-15", "Missing .gitignore", str(p))
    else:
        result.ok("PPV-15", ".gitignore present")


# ─── PPV-16: LowCode downstream path also used for non-LowCode (shared) ──────
def check_ppv_16_shared_downstream_path(pipeline_stages: list[str], result: PpvResult) -> None:
    """Verify that manifest_generation and expected_output stages are present for both pipeline types."""
    required = {"manifest_generation", "expected_output_generation", "pr_packet_generation"}
    present = set(pipeline_stages)
    missing = required - present
    if missing:
        result.fail("PPV-16", f"Shared downstream stages missing from pipeline: {sorted(missing)}")
    else:
        result.ok("PPV-16", "All shared downstream stages present in pipeline")


def run_all_ppv_checks(
    pr_packet: dict,
    example_dirs: list[Path],
    repo_root: Path,
    family: str,
    namespace_source: str,
    registry_entries: list[dict] | None = None,
    pipeline_stages: list[str] | None = None,
) -> PpvResult:
    """Run all PPV checks and return a PpvResult."""
    result = PpvResult()

    check_ppv_01_pr_title_no_lowcode(pr_packet, result)
    check_ppv_02_pr_body_no_lowcode(pr_packet, result)
    check_ppv_03_branch_naming_warn(pr_packet, result)
    check_ppv_07_dir_packages_props(repo_root, result)
    check_ppv_09_root_readme(repo_root, result)
    check_ppv_10_ci_workflow(repo_root, result)
    check_ppv_15_gitignore(repo_root, result)

    for ex_dir in example_dirs:
        slug = ex_dir.name
        check_ppv_04_manifest_exists(ex_dir, result)
        check_ppv_05_expected_output_exists(ex_dir, result)
        check_ppv_06_output_validation_not_only_contract(ex_dir, result)
        csproj_candidates = list(ex_dir.glob("*.csproj"))
        for csproj in csproj_candidates:
            check_ppv_08_csproj_no_version(csproj, result)
        check_ppv_11_folder_layout(ex_dir, family, slug, namespace_source, result)
        check_ppv_12_fixture_provenance(ex_dir, result)
        check_ppv_13_manifest_namespace_source(ex_dir, namespace_source, result)

    for entry in registry_entries or []:
        check_ppv_14_status_not_inflated(entry, result)

    check_ppv_16_shared_downstream_path(pipeline_stages or [], result)

    return result
