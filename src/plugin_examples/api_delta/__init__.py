"""API delta engine — detect changes between catalog versions."""

from plugin_examples.api_delta.delta_engine import compute_delta
from plugin_examples.api_delta.impact_mapper import map_impact

__all__ = ["compute_delta", "map_impact"]
