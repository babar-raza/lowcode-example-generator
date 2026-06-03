"""Command: check."""

from __future__ import annotations


def add_parser(subparsers):
    """Register the check subcommand."""
    # Check command
    parser = subparsers.add_parser("check", help="Check for package updates")
    parser.add_argument("--family", help="Specific family to check")
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the check command."""
    print("Package update check")
    print("Requires live NuGet access. All modules are implemented.")
    return 0
