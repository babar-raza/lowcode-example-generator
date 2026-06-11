"""Canonical scenario-id ↔ destination-repo-path mapping.

Resolves the two known defects in Sprint 59 destination audits:

1. Double-family-prefix bug (diagram family):
   The diagram destination repo dirs follow `{family}-{type}` naming, so
   `diagram-diagram-converter` is the dir name. Constructing scenario_id as
   `family + "-" + dir_name` produces `diagram-diagram-diagram-converter`
   (triple prefix). Fix: use the dir name directly as scenario_id for
   families where dir names already encode the family prefix.

2. PdfAConverter ID normalization mismatch:
   - Pipeline/lifecycle canonical ID: `pdf-pdf-aconverter`
   - Destination repo dir: `pdfa-converter` → constructed id: `pdf-pdfa-converter`
   These refer to the same example. A canonical alias map resolves this.

Usage::

    mapper = DestinationIdMapper()
    scenario_id = mapper.dir_name_to_scenario_id("diagram", "diagram-pdf-converter")
    # Returns: "diagram-pdf-converter"  (not "diagram-diagram-pdf-converter")

    scenario_id = mapper.dir_name_to_scenario_id("pdf", "pdfa-converter")
    # Returns: "pdf-pdf-aconverter"  (not "pdf-pdfa-converter")
"""

from __future__ import annotations

# Families where the destination repo dir name already encodes the family prefix.
# For these families: scenario_id = dir_name (do NOT prepend family again).
FAMILIES_WITH_PREFIXED_DIRS: frozenset[str] = frozenset({"diagram"})

# Explicit alias map: repo_dir_name → canonical_scenario_id
# Used when the pipeline naming convention differs from the repo dir naming convention.
# Key: "{family}/{dir_name}"  Value: canonical scenario_id
REPO_DIR_ALIAS_MAP: dict[str, str] = {
    "pdf/pdfa-converter": "pdf-pdf-aconverter",
}

# Policies for result-collection-output APIs.
# These APIs don't write to a named output file with an extension;
# they return output via ResultCollection. The `output_format` claim is
# proved by API contract, not by a literal file extension in Program.cs.
RESULT_COLLECTION_OUTPUT_APIS: frozenset[str] = frozenset(
    {
        "pdf-image-extractor",  # ImageExtractor → ResultCollection contains PNG images
        "pdf-text-extractor",  # TextExtractor → StringResult (text, no file)
    }
)


class DestinationIdMapper:
    """Maps destination repo example directory names to canonical scenario IDs.

    Accounts for:
    - Families where dir names include the family prefix (diagram)
    - Known naming-convention mismatches (pdfa-converter ↔ pdf-pdf-aconverter)
    """

    def dir_name_to_scenario_id(self, family: str, dir_name: str) -> str:
        """Return the canonical scenario_id for a destination repo example dir.

        Args:
            family: Family name (e.g., "diagram", "pdf").
            dir_name: Directory name from the destination repo
                (e.g., "diagram-diagram-converter", "pdfa-converter").

        Returns:
            Canonical scenario_id as used in lifecycle records and scenario catalog.
        """
        alias_key = f"{family}/{dir_name}"
        if alias_key in REPO_DIR_ALIAS_MAP:
            return REPO_DIR_ALIAS_MAP[alias_key]

        if family in FAMILIES_WITH_PREFIXED_DIRS:
            # Dir name already includes family prefix — use as-is
            return dir_name

        # Standard: prepend family prefix
        return f"{family}-{dir_name}"

    def scenario_id_to_dir_name(self, scenario_id: str, family: str) -> str:
        """Return the destination repo dir name for a canonical scenario_id.

        Args:
            scenario_id: Canonical scenario_id.
            family: Family name.

        Returns:
            Directory name in the destination repo.
        """
        # Check reverse alias map
        for alias_key, canonical in REPO_DIR_ALIAS_MAP.items():
            if canonical == scenario_id:
                # alias_key is "{family}/{dir_name}"
                _, dir_name = alias_key.split("/", 1)
                return dir_name

        if family in FAMILIES_WITH_PREFIXED_DIRS:
            return scenario_id  # dir name = full scenario_id

        # Standard: strip family prefix
        prefix = f"{family}-"
        if scenario_id.startswith(prefix):
            return scenario_id[len(prefix) :]
        return scenario_id

    def is_double_family_prefix(self, family: str, scenario_id: str) -> bool:
        """Return True if scenario_id has the family prefix applied more than once as a bug.

        Detects the Sprint 59 construction error where the audit prepended the
        family prefix to a dir name that already contained the family prefix,
        resulting in a triple occurrence: "diagram-diagram-diagram-converter".

        Note: "diagram-diagram-converter" is the *canonical* id for the
        DiagramConverter type — it starts with "diagram-diagram-" intentionally
        and is NOT a bug. Only three consecutive family segments indicate the error.
        """
        triple_prefix = f"{family}-{family}-{family}-"
        return scenario_id.startswith(triple_prefix)

    def is_result_collection_output(self, scenario_id: str) -> bool:
        """Return True if this scenario uses ResultCollection output (not file path)."""
        return scenario_id in RESULT_COLLECTION_OUTPUT_APIS
