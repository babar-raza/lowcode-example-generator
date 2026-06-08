"""CLI command modules for plugin-examples."""

from __future__ import annotations


def register_all(subparsers):
    """Register all subcommands with the given subparsers object."""
    from plugin_examples.commands.status import add_parser as _status
    _status(subparsers)
    from plugin_examples.commands.run import add_parser as _run
    _run(subparsers)
    from plugin_examples.commands.discover_lowcode import add_parser as _discover_lowcode
    _discover_lowcode(subparsers)
    from plugin_examples.commands.validate_publish_targets import add_parser as _validate_publish_targets
    _validate_publish_targets(subparsers)
    from plugin_examples.commands.resolve_repo_access import add_parser as _resolve_repo_access
    _resolve_repo_access(subparsers)
    from plugin_examples.commands.probe_publish_permissions import add_parser as _probe_publish_permissions
    _probe_publish_permissions(subparsers)
    from plugin_examples.commands.publish_pr import add_parser as _publish_pr
    _publish_pr(subparsers)
    from plugin_examples.commands.merge_pr import add_parser as _merge_pr
    _merge_pr(subparsers)
    from plugin_examples.commands.release_status import add_parser as _release_status
    _release_status(subparsers)
    from plugin_examples.commands.sync_taskcard_docs import add_parser as _sync_taskcard_docs
    _sync_taskcard_docs(subparsers)
    from plugin_examples.commands.render_root_readme import add_parser as _render_root_readme
    _render_root_readme(subparsers)
    from plugin_examples.commands.publish_readme import add_parser as _publish_readme
    _publish_readme(subparsers)
    from plugin_examples.commands.check import add_parser as _check
    _check(subparsers)
    from plugin_examples.commands.publish_pr_batch import add_parser as _publish_pr_batch
    _publish_pr_batch(subparsers)
    from plugin_examples.commands.formimporter_watch import add_parser as _formimporter_watch
    _formimporter_watch(subparsers)
    from plugin_examples.commands.post_publication_verify import add_parser as _post_publication_verify
    _post_publication_verify(subparsers)
    from plugin_examples.commands.version_drift import add_parser as _version_drift
    _version_drift(subparsers)
    from plugin_examples.commands.target_repo_health import add_parser as _target_repo_health
    _target_repo_health(subparsers)
    from plugin_examples.commands.execute_next_actions import add_parser as _execute_next_actions
    _execute_next_actions(subparsers)
    from plugin_examples.commands.next_actions import add_parser as _next_actions
    _next_actions(subparsers)
    from plugin_examples.commands.catalog_discover import add_parser as _catalog_discover
    _catalog_discover(subparsers)
