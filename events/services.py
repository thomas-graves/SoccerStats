"""
Service helpers for the events app.

This module contains pure helper logic that will later be used by the
event replay / stat derivation workflow.

For now, it provides:
- position group classification
- macro formation derivation from current on-pitch positions
- exact position snapshot normalization

These helpers do not touch the database directly.
"""

from collections import Counter


# Position groupings used for formation derivation.
#
# The goalkeeper is intentionally excluded from the macro formation string,
# so a lineup like:
#   GK, RB, CB, CB, LB, RM, CM, CM, LM, ST, ST
# becomes:
#   4-4-2
DEFENSIVE_POSITIONS = {
    "CB",
    "RB",
    "LB",
    "RWB",
    "LWB",
}

MIDFIELD_POSITIONS = {
    "CDM",
    "CM",
    "RM",
    "LM",
    "CAM",
}

ATTACKING_POSITIONS = {
    "CF",
    "RS",
    "LS",
    "RW",
    "LW",
    "ST",
}

GOALKEEPER_POSITIONS = {
    "GK",
}


def get_position_unit(position_label: str) -> str | None:
    """
    Return the broad tactical unit for a position label.

    Possible return values:
    - "DEF"
    - "MID"
    - "ATK"
    - "GK"
    - None for unknown / unsupported labels
    """
    if position_label in DEFENSIVE_POSITIONS:
        return "DEF"
    if position_label in MIDFIELD_POSITIONS:
        return "MID"
    if position_label in ATTACKING_POSITIONS:
        return "ATK"
    if position_label in GOALKEEPER_POSITIONS:
        return "GK"
    return None


def normalize_position_snapshot(position_labels: list[str]) -> list[str]:
    """
    Return a normalized exact position snapshot.

    This keeps only non-empty labels and preserves the current ordering
    passed in by the caller. Later, the derivation engine can decide what
    canonical ordering to use for display or storage.

    Example:
        ["GK", "CB", "CB", "", "LB", "CM"]
    becomes:
        ["GK", "CB", "CB", "LB", "CM"]
    """
    return [label for label in position_labels if label]


def derive_macro_formation(position_labels: list[str]) -> str:
    """
    Derive a simple macro formation string from a list of position labels.

    The formation is derived by counting:
    - defensive roles
    - midfield roles
    - attacking roles

    Goalkeepers are intentionally excluded from the returned string.

    Example:
        ["GK", "CB", "CB", "RB", "LB", "CM", "CM", "RM", "LM", "RS", "LS"]
    returns:
        "4-4-2"

    Notes:
    - This is intentionally a simplified formation derivation.
    - More detailed formation representation can later use the exact
      position snapshot alongside this macro formation.
    """
    unit_counts = Counter()

    for position_label in position_labels:
        unit = get_position_unit(position_label)
        if unit in {"DEF", "MID", "ATK"}:
            unit_counts[unit] += 1

    return f"{unit_counts['DEF']}-{unit_counts['MID']}-{unit_counts['ATK']}"

