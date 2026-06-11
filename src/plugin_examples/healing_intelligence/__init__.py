"""Persistent healing intelligence for the LowCode Example Generator pipeline.

Provides access to committed failure patterns, repair strategies, semantic
steering knowledge, and validator rules — preventing re-discovery of known
failures across pipeline runs and sessions.
"""

from plugin_examples.healing_intelligence.loader import HealingIntelligenceLoader

__all__ = ["HealingIntelligenceLoader"]
