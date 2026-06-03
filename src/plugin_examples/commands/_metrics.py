"""Shared metrics helpers for CLI commands."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def _add_metrics_flags(parser: argparse.ArgumentParser) -> None:
    """Add shared metrics flags to any subparser."""
    parser.add_argument("--metrics", action="store_true",
                        help="Enable metrics collection (dry-run by default)")
    parser.add_argument("--metrics-post", action="store_true",
                        help="POST metrics to API (requires AGENT_METRICS_TOKEN)")
    parser.add_argument("--metrics-job-type", metavar="TYPE",
                        help="Override job_type (e.g., 'Test' for test rows)")
    parser.add_argument("--metrics-strict", action="store_true",
                        help="Fail pipeline on metrics errors")
    parser.add_argument("--metrics-force-repost", action="store_true",
                        help="Bypass ledger duplicate check")
    parser.add_argument("--metrics-config", metavar="PATH",
                        help="Override metrics config path (default: pipeline/configs/metrics.yml)")


def _create_metrics_session(args, *, command: str, family: str = "",
                             repo_root: Path | None = None):
    """Create a MetricsSession from CLI args if metrics are enabled.

    Returns (session, collector) or (None, None).
    """
    metrics_enabled = (
        getattr(args, "metrics", False)
        or os.environ.get("AGENT_METRICS_ENABLED", "").lower() == "true"
    )
    if not metrics_enabled:
        return None, None

    from plugin_examples.metrics.models import MetricsCollector
    from plugin_examples.metrics.config import load_metrics_config
    from plugin_examples.metrics.session import MetricsSession

    collector = MetricsCollector()
    config_path = None
    if getattr(args, "metrics_config", None):
        config_path = Path(args.metrics_config)
    config = load_metrics_config(config_path=config_path)

    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_id = f"metrics-{command}-{family or 'global'}-{ts}"

    # Create evidence dir for non-run commands
    evidence_dir = repo_root / "workspace" / "runs" / run_id / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    session = MetricsSession(
        command=command,
        family=family,
        config=config,
        collector=collector,
        dry_run=not getattr(args, "metrics_post", False),
        post=getattr(args, "metrics_post", False),
        job_type_override=getattr(args, "metrics_job_type", None),
        force_repost=getattr(args, "metrics_force_repost", False),
        strict=getattr(args, "metrics_strict", False),
        evidence_dir=evidence_dir,
        repo_root=repo_root,
        run_id=run_id,
    )
    session.start()
    return session, collector


def _finalize_metrics_session(session, **kwargs) -> dict | None:
    """Finalize a metrics session and print status. Returns result or None."""
    if session is None:
        return None
    result = session.finalize(**kwargs)
    if result.get("post_result", {}).get("posted"):
        print("Metrics: posted successfully")
    elif result.get("error"):
        print(f"Metrics: error — {result['error']}")
    else:
        reason = result.get("post_result", {}).get("reason", "dry_run")
        print(f"Metrics: not posted ({reason})")
    return result
