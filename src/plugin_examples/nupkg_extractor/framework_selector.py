"""Target framework selection from .nupkg lib/ folder contents."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Windows-only .NET Framework TFMs (not .NET Core / .NET 5+)
# Matches net20, net35, net40, net45, net451, net452, net46, net461, net462,
# net47, net471, net472, net48, net481, etc.
_WINDOWS_ONLY_RE = re.compile(r"^net\d{2,3}$")


@dataclass(frozen=True)
class FrameworkSelection:
    selected_framework: str
    selection_reason: str
    requires_windows_runner: bool


def select_framework(
    available_frameworks: list[str],
    preference_order: list[str],
) -> FrameworkSelection:
    """Select the best framework from available lib/ folders.

    Args:
        available_frameworks: TFM folder names found in the .nupkg lib/ directory.
        preference_order: Ordered preference list from family config.

    Returns:
        FrameworkSelection with the chosen TFM and metadata.

    Raises:
        ValueError: If no matching framework is found.
    """
    if not available_frameworks:
        raise ValueError("No frameworks available in .nupkg lib/ directory")

    # Normalize to lowercase for matching
    available_lower = {f.lower(): f for f in available_frameworks}

    for preferred in preference_order:
        key = preferred.lower()
        if key in available_lower:
            original = available_lower[key]
            is_windows = _is_windows_only(key)
            return FrameworkSelection(
                selected_framework=original,
                selection_reason=(
                    f"Matched preference #{preference_order.index(preferred) + 1}: "
                    f"{preferred}"
                ),
                requires_windows_runner=is_windows,
            )

    raise ValueError(
        f"No supported framework found. "
        f"Available: {available_frameworks}, "
        f"Preference: {preference_order}"
    )


def _is_windows_only(tfm_lower: str) -> bool:
    """Check if a TFM requires Windows (classic .NET Framework)."""
    return bool(_WINDOWS_ONLY_RE.match(tfm_lower))
