"""Extract mutation testing results from .mutmut-cache SQLite database.

Used by .github/workflows/mutation-testing.yml to produce a JSON artifact.
Avoids bash heredoc syntax which breaks YAML literal block scalars.

TC-SRHP-22: Fix for broken regex approach that never matched the `🎉 N` format.
"""

import json
import sqlite3
import sys

try:
    c = sqlite3.connect(".mutmut-cache")
    # Collect all status counts via GROUP BY — handles both mutmut 2.x status
    # naming ('ok_killed', 'ok_survived', 'bad_timeout') and any other variants.
    rows = c.execute("SELECT status, COUNT(*) FROM Mutant GROUP BY status").fetchall()
    status_counts: dict[str, int] = dict(rows)
    # Diagnostic: include raw status map in artifact for future auditing
    raw_statuses = dict(status_counts)

    def _get(primary: str, *fallbacks: str) -> int:
        for key in (primary, *fallbacks):
            if key in status_counts:
                return status_counts[key]
        return 0

    killed = _get("ok_killed", "Killed", "killed")
    survived = _get("ok_survived", "Survived", "survived")
    timeout = _get("bad_timeout", "Timeout", "timeout")
    total = killed + survived + timeout
    score = f"{killed / total * 100:.1f}%" if total > 0 else "N/A"
    print(json.dumps({
        "killed": killed,
        "survived": survived,
        "timeout": timeout,
        "total": total,
        "score": score,
        "raw_statuses": raw_statuses,
    }))
except Exception as e:
    print(json.dumps({
        "killed": 0,
        "survived": 0,
        "timeout": 0,
        "total": 0,
        "score": "N/A",
        "error": str(e),
    }))
    sys.exit(0)  # Non-fatal: artifact with error is still valid evidence
