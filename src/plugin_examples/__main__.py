"""Entry point for the plugin examples pipeline."""

import argparse
import logging
import sys

from plugin_examples.observability import configure_logging


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="plugin-examples",
        description="Aspose .NET Plugin Example Generation Pipeline",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    subparsers = parser.add_subparsers(dest="command")

    from plugin_examples.commands import register_all

    register_all(subparsers)

    args = parser.parse_args()

    configure_logging(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
