"""Example generator — build, generate, and validate C# examples."""

from plugin_examples.generator.packet_builder import build_packet
from plugin_examples.generator.code_generator import generate_example
from plugin_examples.generator.project_generator import generate_project
from plugin_examples.generator.manifest_writer import write_example_index

__all__ = ["build_packet", "generate_example", "generate_project", "write_example_index"]
