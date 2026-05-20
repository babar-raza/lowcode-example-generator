"""FormatContract model — the canonical format authority for a LowCode type."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class FormatContract:
    """API-backed format contract for a single LowCode type.

    This is the ONLY authoritative source for format decisions.
    All pipeline components (planner, codegen, templates, manifests, gates,
    README rendering, publication) must derive format from this contract.
    """

    family: str
    type_name: str
    operation_kind: str
    input_format: str
    input_cardinality: str
    canonical_output_format: str
    output_cardinality: str
    output_kind: str  # "file" | "directory" | "stdout" | "stream" | "collection" | "none"
    method_signature: str = ""
    options_class: str | None = None
    alternate_output_formats: tuple[str, ...] = ()
    evidence_confidence: str = "api_verified"
    notes: str = ""

    @property
    def contract_id(self) -> str:
        return f"{self.family}/{self.type_name}"

    @property
    def contract_hash(self) -> str:
        data = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["contract_id"] = self.contract_id
        d["contract_hash"] = self.contract_hash
        return d

    @classmethod
    def from_dict(cls, d: dict) -> FormatContract:
        alt = d.get("alternate_output_formats", [])
        if isinstance(alt, list):
            alt = tuple(alt)
        return cls(
            family=d["family"],
            type_name=d["type_name"],
            operation_kind=d["operation_kind"],
            input_format=d["input_format"],
            input_cardinality=d["input_cardinality"],
            canonical_output_format=d["canonical_output_format"],
            output_cardinality=d["output_cardinality"],
            output_kind=d["output_kind"],
            method_signature=d.get("method_signature", ""),
            options_class=d.get("options_class"),
            alternate_output_formats=alt,
            evidence_confidence=d.get("evidence_confidence", "api_verified"),
            notes=d.get("notes", ""),
        )

    def validate(self) -> list[str]:
        """Return list of validation errors (empty = valid)."""
        errors = []
        if not self.family:
            errors.append("family is required")
        if not self.type_name:
            errors.append("type_name is required")
        if not self.operation_kind:
            errors.append("operation_kind is required")
        if not self.input_format:
            errors.append("input_format is required")
        if not self.input_cardinality:
            errors.append("input_cardinality is required")
        valid_output_kinds = ("file", "directory", "stdout", "stream", "collection", "none")
        if self.output_kind not in valid_output_kinds:
            errors.append(f"output_kind must be one of {valid_output_kinds}, got {self.output_kind!r}")
        if self.canonical_output_format == ".out":
            errors.append("canonical_output_format must not be .out")
        if self.output_kind == "file" and not self.canonical_output_format:
            # file output must have an extension (unless multi like ImageExtractor)
            if self.output_cardinality != "multi":
                pass  # some multi-output types have canonical
        if self.output_kind == "stdout" and self.canonical_output_format:
            errors.append("stdout output should have empty canonical_output_format")
        return errors
