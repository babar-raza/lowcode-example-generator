"""Verification bridge — local .NET validation and example-reviewer integration."""

from plugin_examples.verifier_bridge.dotnet_runner import run_dotnet_validation
from plugin_examples.verifier_bridge.output_validator import validate_output
from plugin_examples.verifier_bridge.bridge import run_example_reviewer

__all__ = ["run_dotnet_validation", "validate_output", "run_example_reviewer"]
