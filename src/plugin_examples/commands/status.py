"""Command: status."""

from __future__ import annotations


def add_parser(subparsers):
    """Register the status subcommand."""
    parser = subparsers.add_parser("status", help="Show pipeline status")
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the status command."""
    print("plugin-examples pipeline — status")
    print("Modules: family_config, nuget_fetcher, nupkg_extractor,")
    print("         reflection_catalog, plugin_detector, api_delta,")
    print("         fixture_registry, example_miner, scenario_planner,")
    print("         llm_router, generator, verifier_bridge, publisher,")
    print("         package_watcher, gates")
    return 0
