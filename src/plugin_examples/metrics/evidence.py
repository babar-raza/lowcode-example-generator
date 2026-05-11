"""Run-scoped evidence writer for agent metrics."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any


def _atomic_json_write(path: Path, data: Any) -> None:
    """Write JSON atomically via tmp + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_llm_calls_jsonl(evidence_dir: Path, calls: list) -> Path:
    """Append per-call records to JSONL file."""
    path = evidence_dir / "agent-metrics-llm-calls.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for call in calls:
            record = asdict(call) if hasattr(call, "__dataclass_fields__") else call
            f.write(json.dumps(record, default=str) + "\n")
    return path


def write_run_summary(evidence_dir: Path, summary: dict) -> Path:
    path = evidence_dir / "agent-metrics-run-summary.json"
    _atomic_json_write(path, summary)
    return path


def write_payload(evidence_dir: Path, payload: dict) -> Path:
    path = evidence_dir / "agent-metrics-payload.json"
    _atomic_json_write(path, payload)
    return path


def write_validation_result(evidence_dir: Path, result: dict) -> Path:
    path = evidence_dir / "agent-metrics-validation.json"
    _atomic_json_write(path, result)
    return path


def write_post_result(evidence_dir: Path, result: dict) -> Path:
    path = evidence_dir / "agent-metrics-post-result.json"
    _atomic_json_write(path, result)
    return path
