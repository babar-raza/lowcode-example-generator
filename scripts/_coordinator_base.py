"""Coordinator base — Wave 25 pilot reusable infrastructure.

Used exclusively by Wave 25. Old wave scripts (W22, W23, W24) are unchanged.
If this proves out, adopt in Wave 26+ and retire the old pattern.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class CoordinatorBase:
    def __init__(self, sprint: str, report_dir: Path, date: str):
        self.sprint = sprint
        self.report_dir = report_dir
        self.date = date

    # ------------------------------------------------------------------ dirs
    def setup_dirs(self, subdirs: list[str]) -> None:
        for sub in subdirs:
            (self.report_dir / sub).mkdir(parents=True, exist_ok=True)
        print(f"[L0] Dirs created under {self.report_dir}")

    # ---------------------------------------------------------------- taskcards
    def write_taskcards(self, tasks: list[tuple[str, str, str]]) -> None:
        """tasks: list of (id, lane, description)"""
        tc = {
            "sprint": self.sprint,
            "date": self.date,
            "generated_at": utcnow(),
            "complete": 0,
            "pending": len(tasks),
            "blocked": 0,
            "taskcards": [
                {
                    "id": t[0],
                    "lane": t[1],
                    "description": t[2],
                    "status": "PENDING",
                    "evidence_path": None,
                    "blocker_class": None,
                    "completed_at": None,
                }
                for t in tasks
            ],
        }
        path = self.report_dir / "taskcards/taskcards.json"
        path.write_text(json.dumps(tc, indent=2), encoding="utf-8")
        print(f"[L0] Taskcards written: {len(tasks)} tasks")

    def update_taskcard(
        self,
        task_id: str,
        status: str,
        evidence_path: str | None = None,
        blocker_class: str | None = None,
    ) -> None:
        tc_path = self.report_dir / "taskcards/taskcards.json"
        tc = json.loads(tc_path.read_text("utf-8"))
        for t in tc["taskcards"]:
            if t["id"] == task_id:
                t["status"] = status
                if evidence_path:
                    t["evidence_path"] = evidence_path
                if blocker_class:
                    t["blocker_class"] = blocker_class
                if status == "COMPLETE":
                    t["completed_at"] = utcnow()
                break
        tc["complete"] = sum(1 for t in tc["taskcards"] if t["status"] == "COMPLETE")
        tc["pending"] = sum(1 for t in tc["taskcards"] if t["status"] == "PENDING")
        tc["blocked"] = sum(1 for t in tc["taskcards"] if t["status"] == "BLOCKED")
        tc_path.write_text(json.dumps(tc, indent=2), encoding="utf-8")

    def bulk_complete(self, updates: dict[str, str]) -> None:
        """updates: {task_id: evidence_path}"""
        for task_id, evidence_path in updates.items():
            self.update_taskcard(task_id, "COMPLETE", evidence_path)

    # --------------------------------------------------------------- ledger
    def write_lane_ledger(self, lanes: dict[str, dict[str, Any]]) -> None:
        ledger = {
            "sprint": self.sprint,
            "date": self.date,
            "generated_at": utcnow(),
            "lanes": lanes,
        }
        path = self.report_dir / "coordinator/lane-ledger.json"
        path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
        print(f"[L0] Lane ledger written: {len(lanes)} lanes")

    # --------------------------------------------------------------- board
    def write_execution_board(self, lanes: dict[str, dict[str, Any]]) -> None:
        board = {
            "sprint": self.sprint,
            "date": self.date,
            "generated_at": utcnow(),
            "total_lanes": len(lanes),
            "lanes_complete": sum(1 for v in lanes.values() if v.get("status") == "COMPLETE"),
            "lanes_in_progress": sum(1 for v in lanes.values() if v.get("status") == "IN_PROGRESS"),
            "lanes_pending": sum(1 for v in lanes.values() if v.get("status") == "PENDING"),
            "lanes": lanes,
        }
        path = self.report_dir / "coordinator/execution-board.json"
        path.write_text(json.dumps(board, indent=2), encoding="utf-8")

    # --------------------------------------------------- hard-stop conditions
    def write_hard_stop_conditions(self, conditions: list[dict[str, Any]]) -> None:
        doc = {
            "sprint": self.sprint,
            "date": self.date,
            "generated_at": utcnow(),
            "total": len(conditions),
            "triggered": 0,
            "conditions": [
                {**c, "triggered": False, "triggered_at": None, "details": None}
                for c in conditions
            ],
        }
        path = self.report_dir / "coordinator/hard-stop-conditions.json"
        path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        print(f"[L0] Hard-stop conditions written: {len(conditions)}")

    # ------------------------------------------ shared file ownership
    def write_shared_file_ownership(self, ownership: list[dict[str, Any]]) -> None:
        doc = {
            "sprint": self.sprint,
            "date": self.date,
            "generated_at": utcnow(),
            "policy": "Each file is owned by exactly one lane. Shared ownership requires explicit joint declaration.",
            "entries": ownership,
        }
        path = self.report_dir / "coordinator/shared-file-ownership.json"
        path.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    # ----------------------------------------------- repo separation
    def write_repo_separation_manifest(
        self,
        publication_repos: list[str],
        fixture_source_repos: list[str],
    ) -> None:
        doc = {
            "sprint": self.sprint,
            "date": self.date,
            "generated_at": utcnow(),
            "policy": (
                "Publication target repos and fixture source repos are strictly separate. "
                "Code that reads fixture source repos must never write to them. "
                "Code that writes to publication target repos must verify URL against allowlist."
            ),
            "publication_target_repos": publication_repos,
            "fixture_source_repos": fixture_source_repos,
            "cross_contamination_check": "PLV-16 and PLV-17 enforce this at runtime",
        }
        path = self.report_dir / "coordinator/repo-separation-manifest.json"
        path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
        print(f"[L0] Repo separation manifest written")
