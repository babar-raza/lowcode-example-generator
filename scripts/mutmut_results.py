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
    killed = c.execute("SELECT COUNT(*) FROM mutant WHERE status='Killed'").fetchone()[0]
    survived = c.execute("SELECT COUNT(*) FROM mutant WHERE status='Survived'").fetchone()[0]
    timeout = c.execute("SELECT COUNT(*) FROM mutant WHERE status='Timeout'").fetchone()[0]
    total = killed + survived + timeout
    score = f"{killed / total * 100:.1f}%" if total > 0 else "N/A"
    print(json.dumps({
        "killed": killed,
        "survived": survived,
        "timeout": timeout,
        "total": total,
        "score": score,
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
