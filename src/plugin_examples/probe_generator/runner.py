"""Probe runner: execute dotnet restore/build/run and classify the outcome.

Probe Failure Taxonomy (5 codes):
  PROBE_FAILED_LICENSE   — zero-byte output + trial/license keywords in stdout/stderr
  PROBE_FAILED_API       — type/method not found at runtime (non-zero exit, not license)
  PROBE_FAILED_BUILD     — dotnet build returned non-zero exit code
  PROBE_FAILED_RESTORE   — dotnet restore failed
  PROBE_FAILED_TIMEOUT   — process exceeded timeout (default 60 seconds)

PR rules enforced here:
  PR-05: output path passed as CLI arg
  PR-06: probe dir is under reports/ (caller responsibility)
  PR-07: timeout on dotnet run (default 60s)
  PR-08: stdout + stderr captured for all phases
  PR-09: output validated (file exists + size > 0)
  PR-10: zero-byte output + license keywords → PROBE_FAILED_LICENSE
"""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

_LICENSE_KEYWORDS = frozenset(["trial", "license", "watermark", "evaluation", "Aspose.License"])

_DEFAULT_TIMEOUT = 60  # seconds


@dataclass
class ProbeResult:
    """Full result of a probe run including all subprocess outputs and taxonomy."""

    restore_ok: bool
    build_ok: bool
    run_ok: bool
    output_validated: bool
    output_size_bytes: int
    log_path: Path | None
    exit_codes: dict = field(default_factory=dict)
    failure_taxonomy: str | None = None
    failure_detail: str = ""
    restore_stdout: str = ""
    restore_stderr: str = ""
    build_stdout: str = ""
    build_stderr: str = ""
    run_stdout: str = ""
    run_stderr: str = ""


class ProbeRunner:
    """Run dotnet restore → build → run and return a classified ProbeResult.

    Args:
        timeout: Timeout in seconds for each subprocess phase.
        output_filename: Name of the expected output file (relative to probe dir).
    """

    def __init__(self, timeout: int = _DEFAULT_TIMEOUT, output_filename: str = "probe-output.bin"):
        self.timeout = timeout
        self.output_filename = output_filename

    def run(self, probe_dir: Path, csproj_path: Path, log_dir: Path | None = None) -> ProbeResult:
        """Run the probe in probe_dir and return a fully-classified ProbeResult.

        Args:
            probe_dir: Directory containing Program.cs and .csproj.
            csproj_path: Path to the .csproj file.
            log_dir: Optional directory to write log files; defaults to probe_dir.

        Returns:
            ProbeResult with all fields populated including failure_taxonomy.
        """
        probe_dir = Path(probe_dir)
        csproj_path = Path(csproj_path)
        if log_dir is None:
            log_dir = probe_dir
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        output_path = probe_dir / self.output_filename
        exit_codes: dict = {}

        # Phase 1: restore
        restore_result = self._run_cmd(
            ["dotnet", "restore", str(csproj_path)],
            cwd=probe_dir,
        )
        restore_ok = restore_result["exit_code"] == 0
        exit_codes["restore"] = restore_result["exit_code"]

        if restore_result.get("timed_out"):
            return ProbeResult(
                restore_ok=False,
                build_ok=False,
                run_ok=False,
                output_validated=False,
                output_size_bytes=0,
                log_path=log_dir / "probe-restore.log",
                exit_codes=exit_codes,
                failure_taxonomy="PROBE_FAILED_TIMEOUT",
                failure_detail="dotnet restore timed out",
                restore_stdout=restore_result["stdout"],
                restore_stderr=restore_result["stderr"],
            )

        if not restore_ok:
            return ProbeResult(
                restore_ok=False,
                build_ok=False,
                run_ok=False,
                output_validated=False,
                output_size_bytes=0,
                log_path=log_dir / "probe-restore.log",
                exit_codes=exit_codes,
                failure_taxonomy="PROBE_FAILED_RESTORE",
                failure_detail=f"dotnet restore exit code {restore_result['exit_code']}",
                restore_stdout=restore_result["stdout"],
                restore_stderr=restore_result["stderr"],
            )

        # Phase 2: build
        build_result = self._run_cmd(
            ["dotnet", "build", str(csproj_path), "--no-restore", "-c", "Release"],
            cwd=probe_dir,
        )
        build_ok = build_result["exit_code"] == 0
        exit_codes["build"] = build_result["exit_code"]

        if build_result.get("timed_out"):
            return ProbeResult(
                restore_ok=restore_ok,
                build_ok=False,
                run_ok=False,
                output_validated=False,
                output_size_bytes=0,
                log_path=log_dir / "probe-build.log",
                exit_codes=exit_codes,
                failure_taxonomy="PROBE_FAILED_TIMEOUT",
                failure_detail="dotnet build timed out",
                restore_stdout=restore_result["stdout"],
                restore_stderr=restore_result["stderr"],
                build_stdout=build_result["stdout"],
                build_stderr=build_result["stderr"],
            )

        if not build_ok:
            return ProbeResult(
                restore_ok=restore_ok,
                build_ok=False,
                run_ok=False,
                output_validated=False,
                output_size_bytes=0,
                log_path=log_dir / "probe-build.log",
                exit_codes=exit_codes,
                failure_taxonomy="PROBE_FAILED_BUILD",
                failure_detail=f"dotnet build exit code {build_result['exit_code']}",
                restore_stdout=restore_result["stdout"],
                restore_stderr=restore_result["stderr"],
                build_stdout=build_result["stdout"],
                build_stderr=build_result["stderr"],
            )

        # Phase 3: run (PR-05: output path as CLI arg)
        run_result = self._run_cmd(
            ["dotnet", "run", "--project", str(csproj_path), "--no-build", "-c", "Release", "--", str(output_path)],
            cwd=probe_dir,
        )
        run_ok = run_result["exit_code"] == 0
        exit_codes["run"] = run_result["exit_code"]

        if run_result.get("timed_out"):
            return ProbeResult(
                restore_ok=restore_ok,
                build_ok=build_ok,
                run_ok=False,
                output_validated=False,
                output_size_bytes=0,
                log_path=log_dir / "probe-run.log",
                exit_codes=exit_codes,
                failure_taxonomy="PROBE_FAILED_TIMEOUT",
                failure_detail="dotnet run timed out",
                restore_stdout=restore_result["stdout"],
                restore_stderr=restore_result["stderr"],
                build_stdout=build_result["stdout"],
                build_stderr=build_result["stderr"],
                run_stdout=run_result["stdout"],
                run_stderr=run_result["stderr"],
            )

        # Phase 4: validate output (PR-09)
        output_size = 0
        output_validated = False
        if output_path.exists():
            output_size = output_path.stat().st_size
            output_validated = output_size > 0

        # Phase 5: classify (PR-10)
        combined_output = (
            run_result["stdout"] + run_result["stderr"] + build_result["stdout"] + build_result["stderr"]
        ).lower()

        taxonomy: str | None = None
        failure_detail = ""

        if not run_ok or not output_validated:
            has_license_keyword = any(kw.lower() in combined_output for kw in _LICENSE_KEYWORDS)
            if output_size == 0 and has_license_keyword:
                taxonomy = "PROBE_FAILED_LICENSE"
                failure_detail = "Zero-byte output with license/trial keywords in output"
            elif not run_ok:
                taxonomy = "PROBE_FAILED_API"
                failure_detail = f"dotnet run exit code {run_result['exit_code']}"
            else:
                taxonomy = "PROBE_FAILED_API"
                failure_detail = "Output file missing or zero bytes"

        return ProbeResult(
            restore_ok=restore_ok,
            build_ok=build_ok,
            run_ok=run_ok,
            output_validated=output_validated,
            output_size_bytes=output_size,
            log_path=log_dir / "probe-run.log",
            exit_codes=exit_codes,
            failure_taxonomy=taxonomy,
            failure_detail=failure_detail,
            restore_stdout=restore_result["stdout"],
            restore_stderr=restore_result["stderr"],
            build_stdout=build_result["stdout"],
            build_stderr=build_result["stderr"],
            run_stdout=run_result["stdout"],
            run_stderr=run_result["stderr"],
        )

    def _run_cmd(self, cmd: list[str], cwd: Path) -> dict:
        """Run a subprocess and return stdout, stderr, exit_code, timed_out."""
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            return {
                "stdout": proc.stdout or "",
                "stderr": proc.stderr or "",
                "exit_code": proc.returncode,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "stdout": (exc.stdout or b"").decode("utf-8", errors="replace")
                if isinstance(exc.stdout, bytes)
                else (exc.stdout or ""),
                "stderr": (exc.stderr or b"").decode("utf-8", errors="replace")
                if isinstance(exc.stderr, bytes)
                else (exc.stderr or ""),
                "exit_code": -1,
                "timed_out": True,
            }
