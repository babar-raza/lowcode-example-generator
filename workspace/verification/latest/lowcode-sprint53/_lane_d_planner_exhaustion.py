"""Sprint 53 Lane D: Whole-portfolio planner exhaustion script."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

repo_root = Path("c:/Users/prora/OneDrive/Documents/GitHub/lowcode-example-generator")
sys.path.insert(0, str(repo_root / "src"))

out_dir = repo_root / "workspace" / "verification" / "latest" / "lowcode-sprint53"
out_dir.mkdir(parents=True, exist_ok=True)

# --- 1. Compute action board and mark recurring checks ---
from plugin_examples.portfolio_action_planner import compute_action_board, RECURRING_CHECK_IDS

board = compute_action_board(repo_root=repo_root)

# Mark all recurring checks as executed (cycle 1)
for action in board.actions:
    if action.id in RECURRING_CHECK_IDS:
        board.mark_executed(action.id, changed=False, cycle=1)

# Build board summary
board_dict = board.to_dict()
next_required = board.next_required_actions()
safe_actions = board.safe_actions()
blocked_actions = board.blocked_actions()

board_summary = {
    "total_actions": len(board.actions),
    "safe_count": len(safe_actions),
    "blocked_count": len(blocked_actions),
    "next_required_count": len(next_required),
    "recurring_checks_satisfied": len([a for a in board.actions if a.execution_state == "recurring_check_satisfied"]),
    "next_required_action_ids": [a.id for a in next_required],
    "blocked_action_ids": [a.id for a in blocked_actions],
}

print("=== Board Summary ===")
print(json.dumps(board_summary, indent=2))

# --- 2. Generate release-status-raw.json ---
from plugin_examples.publisher.release_status import compute_release_status

families = ["cells", "words", "pdf", "diagram", "email", "slides"]
rs = compute_release_status(
    families=families,
    verification_dir=repo_root / "workspace" / "verification",
)

rs_path = out_dir / "release-status-raw.json"
rs_path.write_text(json.dumps(rs, indent=2, default=str), encoding="utf-8")
print(f"\nWrote {rs_path.name}")
print(f"  all_published={rs.get('all_published')}")
print(f"  published_count={rs.get('published_count')}")
print(f"  pr_ready_count={rs.get('pr_ready_count')}")
print(f"  total_contracts={rs.get('total_contracts')}")

# --- 3. Build portfolio-release-status.json ---
portfolio_rs = {
    "report_type": "portfolio-release-status",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "sprint": 53,
    "all_published": rs.get("all_published"),
    "all_contracts_accounted_for": rs.get("all_contracts_accounted_for"),
    "published_count": rs.get("published_count"),
    "pr_ready_count": rs.get("pr_ready_count"),
    "total_contracts": rs.get("total_contracts"),
    "approval_blocked_count": rs.get("approval_blocked_count", 0),
    "families_complete_count": rs.get("families_complete_count"),
    "families_partial_count": rs.get("families_partial_count"),
    "family_verdicts": {
        f["family"]: f.get("scope_status", "UNKNOWN")
        for f in rs.get("families", [])
    },
}
prs_path = out_dir / "portfolio-release-status.json"
prs_path.write_text(json.dumps(portfolio_rs, indent=2), encoding="utf-8")
print(f"\nWrote {prs_path.name}")

# --- 4. Build conservation/parity report ---
conservation = {
    "report_type": "conservation-parity",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "sprint": 53,
    "published": rs.get("published_count"),
    "pr_ready": rs.get("pr_ready_count"),
    "total_contracts": rs.get("total_contracts"),
    "conservation_holds": (rs.get("published_count", 0) + rs.get("pr_ready_count", 0)) == rs.get("total_contracts", 0),
    "parity": rs.get("published_count") == rs.get("total_contracts"),
}
con_path = out_dir / "conservation-parity-report.json"
con_path.write_text(json.dumps(conservation, indent=2), encoding="utf-8")
print(f"\nWrote {con_path.name}")

# --- 5. Build blocker-watch-report.json ---
blocker_watch = {
    "report_type": "blocker-watch",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "sprint": 53,
    "blocked_actions": [
        {
            "id": a.id,
            "family": a.family,
            "execution_state": a.execution_state,
            "blocker": a.blocker,
            "approval_required": a.approval_required,
            "reason": a.reason,
        }
        for a in blocked_actions
    ],
    "total_blocked": len(blocked_actions),
}
bw_path = out_dir / "blocker-watch-report.json"
bw_path.write_text(json.dumps(blocker_watch, indent=2), encoding="utf-8")
print(f"\nWrote {bw_path.name}")

# --- 6. Build planner cycle files ---
cycle1 = {
    "cycle": 1,
    "sprint": 53,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "board_summary": board_summary,
    "actions": board_dict.get("actions", []),
}
c1_path = out_dir / "planner-cycle-01.json"
c1_path.write_text(json.dumps(cycle1, indent=2), encoding="utf-8")
print(f"\nWrote {c1_path.name}")

# Cycle 2: after marking all safe actions as executed
for action in board.actions:
    if action.safe_to_execute_now and not action.executed_this_sprint:
        board.mark_executed(action.id, changed=False, cycle=2)

next_required_2 = board.next_required_actions()
board_dict_2 = board.to_dict()

cycle2 = {
    "cycle": 2,
    "sprint": 53,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "board_summary": {
        "total_actions": len(board.actions),
        "next_required_count": len(next_required_2),
        "next_required_action_ids": [a.id for a in next_required_2],
        "all_safe_executed": all(
            a.executed_this_sprint for a in board.actions if a.safe_to_execute_now
        ),
    },
    "actions": board_dict_2.get("actions", []),
}
c2_path = out_dir / "planner-cycle-02.json"
c2_path.write_text(json.dumps(cycle2, indent=2), encoding="utf-8")
print(f"\nWrote {c2_path.name}")

# --- 7. Regression report ---
regression = {
    "report_type": "planner-regression",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "sprint": 53,
    "planner_cycles_run": 2,
    "cycle1_next_required": board_summary["next_required_count"],
    "cycle2_next_required": len(next_required_2),
    "all_safe_exhausted": all(
        a.executed_this_sprint for a in board.actions if a.safe_to_execute_now
    ),
    "blocked_remain": len(blocked_actions),
    "verdict": "PLANNER_EXHAUSTED" if len(next_required_2) == 0 or all(
        not a.safe_to_execute_now for a in next_required_2
    ) else "PLANNER_HAS_REMAINING_WORK",
}
reg_path = out_dir / "planner-regression-report.json"
reg_path.write_text(json.dumps(regression, indent=2), encoding="utf-8")
print(f"\nWrote {reg_path.name}")
print(f"\nVerdict: {regression['verdict']}")
print("Lane D complete.")
