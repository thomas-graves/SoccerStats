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

from lineups.models import LineupEntry, LineupRoleChoices


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


def build_position_state(entries: list[tuple[object, str]]) -> dict[object, str]:
    """
    Build the current on-pitch position state from ordered `(participant_key, position_label)` pairs.

    The returned mapping preserves insertion order, which gives us a stable
    exact position snapshot for later UI and derivation work.

    Example:
        [
            (101, "GK"),
            (102, "CB"),
            (103, "CB"),
            (104, "RB"),
        ]

    becomes:
        {
            101: "GK",
            102: "CB",
            103: "CB",
            104: "RB",
        }

    Notes:
    - `participant_key` is intentionally generic for now. Later it will usually
      be a `LineupEntry` primary key.
    - Blank position labels are ignored.
    - If the same participant key appears twice, the later value wins.
    """
    position_state: dict[object, str] = {}

    for participant_key, position_label in entries:
        if not position_label:
            continue
        position_state[participant_key] = position_label

    return position_state


def get_exact_position_snapshot(position_state: dict[object, str]) -> list[tuple[object, str]]:
    """
    Return the exact ordered position snapshot from the current on-pitch state.

    This preserves the current insertion order of the state mapping and is
    intended for future detailed formation / tactical UI work.

    Example:
        {
            101: "GK",
            102: "CB",
            103: "CB",
            104: "RB",
        }

    returns:
        [
            (101, "GK"),
            (102, "CB"),
            (103, "CB"),
            (104, "RB"),
        ]
    """
    return list(position_state.items())


def derive_macro_formation_from_state(position_state: dict[object, str]) -> str:
    """
    Derive a macro formation string from the current on-pitch position state.

    This is a thin wrapper around `derive_macro_formation(...)` that works
    directly from the state mapping used during event replay.
    """
    return derive_macro_formation(list(position_state.values()))


def apply_substitution(
    position_state: dict[object, str],
    subbed_off_key: object,
    subbed_on_key: object,
    subbed_on_position: str,
) -> dict[object, str]:
    """
    Apply a substitution to the current on-pitch position state.

    Rules:
    - the subbed-off participant must currently be on the pitch
    - the subbed-on participant must not already be on the pitch
    - the subbed-on position must be provided

    Returns a new state mapping and does not mutate the input state.
    """
    if subbed_off_key not in position_state:
        raise ValueError("Subbed-off participant is not currently in the on-pitch state.")

    if subbed_on_key in position_state:
        raise ValueError("Subbed-on participant is already present in the on-pitch state.")

    if not subbed_on_position:
        raise ValueError("Subbed-on position must be provided.")

    new_state = dict(position_state)
    del new_state[subbed_off_key]
    new_state[subbed_on_key] = subbed_on_position
    return new_state


def apply_position_change(
    position_state: dict[object, str],
    actor_key: object,
    position_to: str,
) -> dict[object, str]:
    """
    Apply a position change to the current on-pitch position state.

    Rules:
    - the actor must currently be on the pitch
    - the new position must be provided

    Returns a new state mapping and does not mutate the input state.
    """
    if actor_key not in position_state:
        raise ValueError("Position-change actor is not currently in the on-pitch state.")

    if not position_to:
        raise ValueError("Position-change target position must be provided.")

    new_state = dict(position_state)
    new_state[actor_key] = position_to
    return new_state


def build_initial_club_position_state(match) -> dict[int, str]:
    """
    Build the initial on-pitch club position state for a match from lineup entries.

    This uses only starter lineup entries, because substitutes begin on the bench
    and only enter the on-pitch state later through substitution events.

    The returned mapping uses LineupEntry primary keys as the participant keys.
    This keeps the replay layer aligned to match-context entities rather than
    raw Player or Registration identifiers.

    Example return value:
        {
            11: "GK",
            12: "CB",
            13: "CB",
            14: "RB",
            15: "LB",
            ...
        }

    Notes:
    - Starter lineup entries are expected to already have non-blank position labels.
      That is enforced by LineupEntry.clean().
    - The ordering comes from the LineupEntry model ordering plus the explicit
      query ordering used below, which gives a stable initial exact snapshot.
    """
    starter_entries = (
        LineupEntry.objects.filter(
            match=match,
            role=LineupRoleChoices.STARTER,
        )
        .exclude(position_label="")
        .order_by("sort_order", "id")
    )

    entries = [
        (lineup_entry.pk, lineup_entry.position_label)
        for lineup_entry in starter_entries
    ]

    return build_position_state(entries)

