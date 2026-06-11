"""Publication lifecycle validators (PLV-01..15) — Wave 22.

Catches wrong-stream evidence, README gaps, branch naming, PR state inflation,
branch cleanup, post-merge state, and more.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PlvResult:
    checks: list[dict] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    warnings: int = 0

    def ok(self, code: str, msg: str) -> None:
        self.checks.append({"code": code, "status": "PASS", "message": msg})
        self.passed += 1

    def fail(self, code: str, msg: str, detail: str = "") -> None:
        self.checks.append({"code": code, "status": "FAIL", "message": msg, "detail": detail})
        self.failed += 1

    def warn(self, code: str, msg: str) -> None:
        self.checks.append({"code": code, "status": "WARN", "message": msg})
        self.warnings += 1


# ── PLV-01: Wrong-stream evidence validator ───────────────────────────────────
def check_plv_01_wrong_stream_evidence(evidence_bundle_name: str, result: PlvResult) -> None:
    """Evidence bundle name must match plugin pipeline naming convention."""
    pattern = r"lowcode-plugin-canonical-package-wave\d+-\d{8}\.zip"
    if not re.match(pattern, evidence_bundle_name):
        result.fail(
            "PLV-01",
            f"Evidence bundle name does not match plugin pipeline pattern: {evidence_bundle_name!r}",
            detail=f"Expected pattern: {pattern}",
        )
    else:
        result.ok("PLV-01", f"Evidence bundle name matches plugin pipeline convention: {evidence_bundle_name}")


# ── PLV-02: Non-LowCode PR title must not say LowCode ─────────────────────────
def check_plv_02_pr_title_no_lowcode(pr_packet: dict, result: PlvResult) -> None:
    ns = pr_packet.get("namespace_source", "LOWCODE")
    title = pr_packet.get("pr_title", "")
    if ns == "NON_LOWCODE_PLUGIN" and re.search(r"feat\s*\(\s*lowcode\s*\)", title, re.IGNORECASE):
        result.fail("PLV-02", f"PR title uses feat(lowcode) for NON_LOWCODE_PLUGIN family: {title!r}")
    else:
        result.ok("PLV-02", "PR title terminology correct")


# ── PLV-03: Non-LowCode branch must not use lowcode/ prefix (warn for legacy) ─
def check_plv_03_branch_naming(pr_packet: dict, result: PlvResult) -> None:
    ns = pr_packet.get("namespace_source", "LOWCODE")
    branch = pr_packet.get("branch_name", "")
    legacy_ok = pr_packet.get("branch_legacy_grandfathered", False)
    if ns == "NON_LOWCODE_PLUGIN" and branch.startswith("lowcode/"):
        if legacy_ok:
            result.warn(
                "PLV-03",
                f"Branch '{branch}' uses lowcode/ prefix (grandfathered legacy; use plugins/ for new branches)",
            )
        else:
            result.fail("PLV-03", f"New branch '{branch}' must not use lowcode/ prefix for NON_LOWCODE_PLUGIN family")
    else:
        result.ok("PLV-03", "Branch naming acceptable")


# ── PLV-04: Every public example must have README.md ─────────────────────────
def check_plv_04_example_readme_exists(example_dir: Path, result: PlvResult) -> None:
    p = example_dir / "README.md"
    if not p.exists():
        result.fail("PLV-04", f"Missing README.md in example directory: {example_dir}", str(example_dir))
    else:
        result.ok("PLV-04", f"README.md present: {example_dir.name}")


# ── PLV-05: README must have required content sections ───────────────────────
def check_plv_05_readme_quality(example_dir: Path, result: PlvResult) -> None:
    p = example_dir / "README.md"
    if not p.exists():
        result.ok("PLV-05", "Skipped (no README to validate)")
        return
    content = p.read_text(encoding="utf-8")
    missing = []
    if "## Purpose" not in content and "## About" not in content and len(content) < 200:
        missing.append("purpose/about section")
    if "## Prerequisites" not in content and "prerequisite" not in content.lower():
        missing.append("prerequisites section")
    if "## Expected Output" not in content and "expected" not in content.lower():
        missing.append("expected output section")
    if missing:
        result.warn("PLV-05", f"README.md in {example_dir.name} is missing: {', '.join(missing)}")
    else:
        result.ok("PLV-05", f"README.md quality sufficient: {example_dir.name}")


# ── PLV-06: Root README must index examples ───────────────────────────────────
def check_plv_06_root_readme_index(repo_root: Path, family: str, slugs: list[str], result: PlvResult) -> None:
    p = repo_root / "README.md"
    if not p.exists():
        result.fail("PLV-06", "Root README.md missing")
        return
    content = p.read_text(encoding="utf-8")
    missing_slugs = [s for s in slugs if s not in content]
    if missing_slugs:
        result.fail("PLV-06", f"Root README.md does not index all examples: missing {missing_slugs}")
    else:
        result.ok("PLV-06", f"Root README.md indexes all {len(slugs)} examples")


# ── PLV-07: PR state: PR_CREATED ≠ MERGED ─────────────────────────────────────
def check_plv_07_pr_state_not_inflated(registry_entry: dict, result: PlvResult) -> None:
    status = registry_entry.get("registry_status", "")
    pr_url = registry_entry.get("pr_url", "")
    merged_at = registry_entry.get("merged_at", "")
    published_at = registry_entry.get("published_at", "")

    if status == "PR_CREATED" and not pr_url:
        result.fail("PLV-07", f"PR_CREATED without pr_url: {registry_entry.get('slug','?')}")
    elif status == "MERGED" and not merged_at:
        result.fail("PLV-07", f"MERGED without merged_at timestamp: {registry_entry.get('slug','?')}")
    elif status == "PUBLISHED" and not published_at:
        result.fail("PLV-07", f"PUBLISHED without published_at timestamp: {registry_entry.get('slug','?')}")
    else:
        result.ok("PLV-07", f"PR status not inflated: {status}")


# ── PLV-08: Branch cleanup: merged PR branch must be deleted or explicitly retained
def check_plv_08_branch_cleanup(
    branch_name: str, is_deleted: bool, is_merged: bool, retention_reason: str, result: PlvResult
) -> None:
    if not is_merged:
        result.ok("PLV-08", f"Branch '{branch_name}' not yet merged — cleanup not required")
        return
    if is_deleted:
        result.ok("PLV-08", f"Branch '{branch_name}' deleted after merge")
    elif retention_reason:
        result.warn("PLV-08", f"Branch '{branch_name}' retained post-merge: {retention_reason}")
    else:
        result.fail("PLV-08", f"Branch '{branch_name}' exists after merge but no retention reason given")


# ── PLV-09: Post-merge state: merged PR must update publication matrix ─────────
def check_plv_09_post_merge_state(registry_entry: dict, result: PlvResult) -> None:
    merged_at = registry_entry.get("merged_at", "")
    status = registry_entry.get("registry_status", "")
    if merged_at and status not in ("MERGED", "BRANCH_CLEANED", "PUBLISHED"):
        result.fail(
            "PLV-09",
            f"PR is merged (merged_at={merged_at}) but registry_status={status!r} not updated",
            detail=registry_entry.get("slug", "?"),
        )
    else:
        result.ok("PLV-09", f"Post-merge state consistent: {status}")


# ── PLV-10: example.manifest.json required ────────────────────────────────────
def check_plv_10_manifest_exists(example_dir: Path, result: PlvResult) -> None:
    p = example_dir / "example.manifest.json"
    if not p.exists():
        result.fail("PLV-10", "Missing example.manifest.json", str(p))
    else:
        result.ok("PLV-10", "example.manifest.json present")


# ── PLV-11: expected-output.json required ─────────────────────────────────────
def check_plv_11_expected_output_exists(example_dir: Path, result: PlvResult) -> None:
    p = example_dir / "expected-output.json"
    if not p.exists():
        result.fail("PLV-11", "Missing expected-output.json", str(p))
    else:
        result.ok("PLV-11", "expected-output.json present")


# ── PLV-12: output-validation.json must not substitute expected-output.json ───
def check_plv_12_ov_not_only_contract(example_dir: Path, result: PlvResult) -> None:
    ov = example_dir / "output-validation.json"
    eo = example_dir / "expected-output.json"
    if ov.exists() and not eo.exists():
        result.fail("PLV-12", "output-validation.json exists but expected-output.json is missing", str(example_dir))
    else:
        result.ok("PLV-12", "output-validation.json does not substitute expected-output.json")


# ── PLV-13: Central package management validator ──────────────────────────────
def check_plv_13_central_package_management(repo_root: Path, result: PlvResult) -> None:
    p = repo_root / "Directory.Packages.props"
    if not p.exists():
        result.fail("PLV-13", "Missing Directory.Packages.props (central package management required)", str(p))
        return
    content = p.read_text(encoding="utf-8")
    if "ManagePackageVersionsCentrally" not in content:
        result.warn("PLV-13", "Directory.Packages.props exists but ManagePackageVersionsCentrally not found")
    else:
        result.ok("PLV-13", "Central package management configured")


# ── PLV-14: Target repo CI/workflow validator ─────────────────────────────────
def check_plv_14_ci_workflow(repo_root: Path, result: PlvResult) -> None:
    wf_dir = repo_root / ".github" / "workflows"
    if not wf_dir.exists() or not any(wf_dir.glob("*.yml")):
        result.fail("PLV-14", "Missing .github/workflows/*.yml CI workflow", str(wf_dir))
        return
    wf_file = next(wf_dir.glob("*.yml"))
    content = wf_file.read_text(encoding="utf-8")
    if "dotnet build" not in content:
        result.warn("PLV-14", f"CI workflow {wf_file.name} does not contain dotnet build step")
    else:
        result.ok("PLV-14", f"CI workflow with dotnet build: {wf_file.name}")


# ── PLV-15: Final evidence authority validator ────────────────────────────────
def check_plv_15_evidence_authority(bundle_path: str, sha_file: str, attestation_file: str, result: PlvResult) -> None:
    from pathlib import Path as P

    b = P(bundle_path)
    s = P(sha_file)
    a = P(attestation_file)
    if not b.exists():
        result.fail("PLV-15", f"Evidence bundle missing: {bundle_path}")
        return
    if not s.exists():
        result.fail("PLV-15", f"SHA sidecar missing: {sha_file}")
        return
    if not a.exists():
        result.fail("PLV-15", f"Final attestation missing: {attestation_file}")
        return
    result.ok("PLV-15", "Evidence authority complete: bundle + sidecar + attestation present")


# ── PLV-16: Fixture source repos never appear as publication targets ───────────
_FIXTURE_SOURCE_REPO_OWNERS = frozenset(
    {
        "aspose-barcode",
        "aspose-svg",
        "aspose-cad",
        "aspose-cells",
        "aspose-words",
        "aspose-html",
        "aspose-font",
        "aspose-imaging",
        "aspose-gis",
        "aspose-finance",
        "aspose-omr",
        "aspose-note",
        "aspose-tasks",
        "aspose-page",
        "aspose-ocr",
        "aspose-3d",
        "aspose-psd",
        "aspose-zip",
    }
)

_APPROVED_PUBLICATION_REPOS = frozenset(
    {
        "aspose-barcode-net/Aspose.BarCode.Plugins-for-.NET-Examples",
        "aspose-svg-net/Aspose.SVG.Plugins-for-.NET-Examples",
        "aspose-cad-net/Aspose.CAD.Plugins-for-.NET-Examples",
    }
)


def check_plv_16_fixture_source_not_publication_target(code_or_config_refs: list[str], result: PlvResult) -> None:
    """Verify no publication code references fixture source repos as write targets.

    ``code_or_config_refs`` is a list of repo strings (owner/repo) that appear
    as PR or merge targets in the code being validated.
    """
    violations = []
    for ref in code_or_config_refs:
        owner = ref.split("/")[0] if "/" in ref else ref
        if owner in _FIXTURE_SOURCE_REPO_OWNERS:
            violations.append(ref)
    if violations:
        result.fail(
            "PLV-16",
            "Fixture source repo(s) referenced as publication targets — HS-11 violation",
            detail=", ".join(violations),
        )
    else:
        result.ok("PLV-16", "No fixture source repo referenced as publication target")


# ── PLV-17: PR URL matches APPROVED_PUBLICATION_REPOS allowlist ───────────────
def check_plv_17_pr_url_allowlist(pr_url: str, result: PlvResult) -> None:
    """Verify PR URL repo is in the approved publication repos allowlist."""
    matched = any(repo in pr_url for repo in _APPROVED_PUBLICATION_REPOS)
    if not matched:
        result.fail(
            "PLV-17",
            f"PR URL {pr_url!r} does not match APPROVED_PUBLICATION_REPOS allowlist",
            detail=f"Allowed: {sorted(_APPROVED_PUBLICATION_REPOS)}",
        )
    else:
        result.ok("PLV-17", f"PR URL matches allowlist: {pr_url!r}")


def run_all_plv_checks(
    evidence_bundle_name: str,
    pr_packet: dict,
    example_dirs: list[Path],
    repo_root: Path,
    family: str,
    slugs: list[str],
    registry_entries: list[dict] | None = None,
    branch_cleanup_records: list[dict] | None = None,
    bundle_path: str = "",
    sha_file: str = "",
    attestation_file: str = "",
    publication_target_refs: list[str] | None = None,
    pr_url: str = "",
) -> PlvResult:
    result = PlvResult()
    check_plv_01_wrong_stream_evidence(evidence_bundle_name, result)
    check_plv_02_pr_title_no_lowcode(pr_packet, result)
    check_plv_03_branch_naming(pr_packet, result)
    for ex_dir in example_dirs:
        check_plv_04_example_readme_exists(ex_dir, result)
        check_plv_05_readme_quality(ex_dir, result)
        check_plv_10_manifest_exists(ex_dir, result)
        check_plv_11_expected_output_exists(ex_dir, result)
        check_plv_12_ov_not_only_contract(ex_dir, result)
    check_plv_06_root_readme_index(repo_root, family, slugs, result)
    check_plv_13_central_package_management(repo_root, result)
    check_plv_14_ci_workflow(repo_root, result)
    for entry in registry_entries or []:
        check_plv_07_pr_state_not_inflated(entry, result)
        check_plv_09_post_merge_state(entry, result)
    for rec in branch_cleanup_records or []:
        check_plv_08_branch_cleanup(
            rec.get("branch", ""),
            rec.get("deleted", False),
            rec.get("merged", False),
            rec.get("retention_reason", ""),
            result,
        )
    if bundle_path:
        check_plv_15_evidence_authority(bundle_path, sha_file, attestation_file, result)
    check_plv_16_fixture_source_not_publication_target(publication_target_refs or [], result)
    if pr_url:
        check_plv_17_pr_url_allowlist(pr_url, result)
    return result
