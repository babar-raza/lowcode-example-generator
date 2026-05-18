"""Source-truth README publication facts for LowCode example repositories.

Extracts verified input/output format claims and source snippets from actual
generated example source files (Program.cs). README rows render from these
verified facts, not from config defaults or name-keyword heuristics.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Regex patterns to extract file extensions from Program.cs path assignments
# Matches: "input.vsdx", 'input.pdf', Path.Combine(workDir, "input.vsdx"), etc.
_INPUT_PATTERN = re.compile(r'["\']input\.(\w+)["\']')
_OUTPUT_PATTERN = re.compile(r'["\']output\.(\w+)["\']')


@dataclass
class ExampleFact:
    """Verified publication fact for a single example."""
    example_name: str
    api_symbol: str
    source_file_path: str
    source_file_sha256: str
    snippet_mode: str  # "full_file" | "excerpt" | "none"
    snippet_content: str
    snippet_content_sha256: str
    input_extension: str
    output_extension: str
    input_extension_source: str  # e.g. "program_cs:line14:input.vsdx"
    output_extension_source: str
    proof_source: str  # "program_cs" | "config" | "blocked_unverified"
    validation_status: str  # "verified" | "blocked_unverified"


@dataclass
class ExampleReadmeFacts:
    """Complete set of verified facts for a family's README."""
    family: str
    generated_at: str
    source_artifact: str
    facts: list[ExampleFact] = field(default_factory=list)


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_extension(pattern: re.Pattern, source: str) -> tuple[str, str]:
    """Extract file extension and source location from Program.cs content.

    Returns (extension, source_location) or ("", "") if not found.
    """
    for i, line in enumerate(source.splitlines(), 1):
        m = pattern.search(line)
        if m:
            ext = m.group(1)
            raw = m.group(0).strip('"').strip("'")
            return ext, f"program_cs:line{i}:{raw}"
    return "", ""


def extract_example_readme_facts(
    family: str,
    package_path: Path,
    examples: list[dict],
    manifest_reader=None,
) -> ExampleReadmeFacts:
    """Extract verified README facts from actual example source files.

    Args:
        family: Family name (e.g. "diagram").
        package_path: Path to the PR dry-run package directory.
        examples: List of example metadata dicts with at least ``name``.
        manifest_reader: Optional callable to read API symbol from manifest.

    Returns:
        ExampleReadmeFacts with one ExampleFact per example.

    Each fact is either ``verified`` (input/output extracted from Program.cs)
    or ``blocked_unverified`` (source could not determine extensions).
    """
    facts = ExampleReadmeFacts(
        family=family,
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_artifact=str(package_path),
    )

    for ex in examples:
        name = ex.get("name", "") or ex.get("scenario_id", "")
        if not name:
            continue

        program_cs = package_path / "examples" / family / "lowcode" / name / "Program.cs"

        if not program_cs.exists():
            facts.facts.append(ExampleFact(
                example_name=name,
                api_symbol="",
                source_file_path=str(program_cs.relative_to(package_path)),
                source_file_sha256="",
                snippet_mode="none",
                snippet_content="",
                snippet_content_sha256="",
                input_extension="",
                output_extension="",
                input_extension_source="",
                output_extension_source="",
                proof_source="blocked_unverified",
                validation_status="blocked_unverified",
            ))
            continue

        source = program_cs.read_text(encoding="utf-8")
        file_hash = _sha256_file(program_cs)

        # Extract extensions from source
        input_ext, input_src = _extract_extension(_INPUT_PATTERN, source)
        output_ext, output_src = _extract_extension(_OUTPUT_PATTERN, source)

        # Determine snippet mode
        line_count = len(source.splitlines())
        if line_count <= 120:
            snippet_mode = "full_file"
            snippet_content = source
        else:
            snippet_mode = "excerpt"
            lines = source.splitlines()
            snippet_content = "\n".join(lines[:80]) + "\n// ... see full source in Program.cs\n"

        # API symbol from manifest if available
        api_symbol = ""
        if manifest_reader:
            manifest_path = (
                package_path / "examples" / family / "lowcode" / name / "example.manifest.json"
            )
            api_symbol = manifest_reader(manifest_path) or ""

        # Validation status
        if input_ext and output_ext:
            validation_status = "verified"
            proof_source = "program_cs"
        else:
            validation_status = "blocked_unverified"
            proof_source = "blocked_unverified"
            logger.warning(
                "Example '%s': could not extract %s from Program.cs",
                name,
                "input extension" if not input_ext else "output extension",
            )

        facts.facts.append(ExampleFact(
            example_name=name,
            api_symbol=api_symbol,
            source_file_path=str(program_cs.relative_to(package_path)),
            source_file_sha256=file_hash,
            snippet_mode=snippet_mode,
            snippet_content=snippet_content,
            snippet_content_sha256=_sha256(snippet_content),
            input_extension=input_ext,
            output_extension=output_ext,
            input_extension_source=input_src,
            output_extension_source=output_src,
            proof_source=proof_source,
            validation_status=validation_status,
        ))

    return facts


def facts_to_json(facts: ExampleReadmeFacts) -> str:
    """Serialize facts to JSON string (without snippet content for evidence)."""
    d = asdict(facts)
    # Strip snippet content from evidence JSON to keep it small
    for f in d.get("facts", []):
        f.pop("snippet_content", None)
    return json.dumps(d, indent=2)
