"""Metrics poster — dry-run safe, persistent ledger, test-only in sprint."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)


def _payload_hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _read_ledger(ledger_path: Path) -> list[dict]:
    if not ledger_path.exists():
        return []
    entries = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _append_ledger(ledger_path: Path, entry: dict, max_entries: int = 500) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    entries = _read_ledger(ledger_path)
    entries.append(entry)
    if len(entries) > max_entries:
        entries = entries[-max_entries // 2 :]
    with open(ledger_path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, default=str) + "\n")


def check_duplicate(
    ledger_path: Path, run_id: str, job_type: str,
) -> bool:
    """Return True if this run_id+job_type already posted (non-dry-run)."""
    for entry in _read_ledger(ledger_path):
        if (entry.get("run_id") == run_id
                and entry.get("job_type") == job_type
                and not entry.get("dry_run", True)):
            return True
    return False


def post_metrics(
    payload: dict,
    config: Any,
    *,
    dry_run: bool = True,
    force_repost: bool = False,
    repo_root: Path | None = None,
    test_only_sprint: bool = True,
) -> dict:
    """Post metrics payload to the API endpoint.

    Returns a result dict documenting what happened.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[3]

    ledger_path = repo_root / config.post_ledger_path
    run_id = payload.get("run_id", "")
    job_type = payload.get("job_type", "")

    # Dry-run: never POST
    if dry_run:
        return {
            "posted": False,
            "reason": "dry_run",
            "dry_run": True,
            "payload_hash": _payload_hash(payload),
        }

    # Sprint safety: block production job_types
    if test_only_sprint and job_type != "Test":
        return {
            "posted": False,
            "reason": f"production job_type '{job_type}' blocked in test-only sprint",
            "dry_run": dry_run,
        }

    # Duplicate check
    if not force_repost and check_duplicate(ledger_path, run_id, job_type):
        return {
            "posted": False,
            "reason": "duplicate_already_posted",
            "run_id": run_id,
            "job_type": job_type,
        }

    # Real POST
    token = os.environ.get(config.env_token_var, "")
    if not token:
        return {
            "posted": False,
            "reason": f"missing env var {config.env_token_var}",
        }

    # Google Apps Script uses token as query parameter
    endpoint = config.api_endpoint
    if "?" in endpoint:
        endpoint = f"{endpoint}&token={token}"
    else:
        endpoint = f"{endpoint}?token={token}"

    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=30,
        )
        http_status = resp.status_code
        response_text = resp.text[:500]
    except Exception as e:
        return {
            "posted": False,
            "reason": "network_error",
            "error": str(e),
        }

    success = 200 <= http_status < 300

    if success:
        _append_ledger(
            ledger_path,
            {
                "run_id": run_id,
                "job_type": job_type,
                "posted_at": datetime.now(timezone.utc).isoformat(),
                "http_status": http_status,
                "payload_hash": _payload_hash(payload),
                "dry_run": False,
            },
            max_entries=config.ledger_max_entries,
        )

    return {
        "posted": success,
        "http_status": http_status,
        "response_preview": response_text,
        "payload_hash": _payload_hash(payload),
    }
