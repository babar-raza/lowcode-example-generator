"""Integration tests for CLI help and subcommand discovery — TC-INTTEST-002."""

from __future__ import annotations

import argparse
import sys

import pytest

from plugin_examples.commands import register_all

EXPECTED_SUBCOMMANDS = [
    "status", "run", "discover-lowcode", "validate-publish-targets",
    "resolve-repo-access", "probe-publish-permissions", "publish-pr",
    "merge-pr", "release-status", "sync-taskcard-docs", "render-root-readme",
    "publish-readme", "check", "publish-pr-batch", "formimporter-watch",
    "post-publication-verify", "version-drift", "target-repo-health",
    "execute-next-actions", "next-actions", "catalog-discover",
    "doctor", "verify-remote",
]


def _build_parser() -> argparse.ArgumentParser:
    """Build the full CLI argument parser."""
    parser = argparse.ArgumentParser(prog="plugin-examples")
    subparsers = parser.add_subparsers(dest="command")
    register_all(subparsers)
    return parser


class TestCliHelp:
    def test_help_flag_produces_output(self, capsys):
        """--help produces usage text and exits cleanly."""
        parser = _build_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--help"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()

    def test_all_subcommands_registered(self):
        """All expected subcommands are registered via register_all."""
        parser = _build_parser()
        # Access subparsers choices
        subparsers_actions = [
            action for action in parser._subparsers._actions
            if isinstance(action, argparse._SubParsersAction)
        ]
        assert len(subparsers_actions) == 1, "Expected exactly one subparsers action"
        registered = set(subparsers_actions[0].choices.keys())
        for cmd in EXPECTED_SUBCOMMANDS:
            assert cmd in registered, f"Subcommand '{cmd}' not registered"

    def test_unknown_subcommand_causes_error(self):
        """Unknown subcommand produces a parse error."""
        parser = _build_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["nonexistent-command-xyz"])
        assert exc_info.value.code != 0

    def test_run_subcommand_requires_family(self):
        """The run subcommand requires --family argument."""
        parser = _build_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["run"])
        assert exc_info.value.code != 0

    def test_run_subcommand_accepts_dry_run(self):
        """The run subcommand accepts --family and --dry-run."""
        parser = _build_parser()
        args = parser.parse_args(["run", "--family", "cells", "--dry-run"])
        assert args.family == "cells"
        assert args.dry_run is True
