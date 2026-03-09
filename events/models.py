"""
Models for the events app.

"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


# These string references point to models in other Django apps.
# Use lazy model references so this app can reference models in other apps
# without creating circular import issues at import time.
MATCH_MODEL = "matches.Match"
TEAM_MODEL = "teams.Team"
PLAYER_MODEL = "players.Player"


class EventPeriod(models.TextChoices):
    """
    Broad match period buckets for ordering and filtering events.

    We store the period separately from minute so that:
    - 10' in the first half and 10' in extra time are distinguishable
    - admin filtering is cleaner
    - future stat derivation is more reliable
    """
    FIRST_HALF = "1H", _("1st Half")
    SECOND_HALF = "2H", _("2nd Half")
    EXTRA_TIME_FIRST = "ET1", _("Extra Time 1st ET Half")
    EXTRA_TIME_SECOND = "ET2", _("2nd ET Half")
    PENALTIES = "PEN", _("Penalties")


class EventOutcome(models.TextChoices):
    """
    A lightweight outcome flag for events where success/failure matters.

    Examples:
    - dribble: success / failure
    - tackle: success / failure
    - shot: success / failure or neutral depending on your workflow
    - kick_off: usually neutral
    """
    SUCCESS = "success", _("Success")
    FAILURE = "failure", _("Failure")
    NEUTRAL = "neutral", _("Neutral")


class EventType(models.TextChoices):
    """
    Canonical list of supported event types.

    These are the top-level event categories that admins will select
    when logging a match event.
    """

    # Match control
    KICK_OFF = "kick_off", _("Kick off")
    HALF_START = "half_start", _("Half start")
    HALF_END = "half_end", _("Half end")
    FULL_TIME = "full_time", _("Full time")
    EXTRA_TIME_START = "extra_time_start", _("Extra time start")
    EXTRA_TIME_END = "extra_time_end", _("Extra time end")
    PENALTIES_START = "penalties_start", _("Penalties start")
    PENALTIES_END = "penalties_end", _("Penalties end")

    # Ball progression
    CARRY = "carry", _("Carry")
    DRIBBLE = "dribble", _("Dribble")
    CROSS = "cross", _("Cross")
    THROUGH_BALL = "through_ball", _("Through ball")
    LONG_BALL = "long_ball", _("Long ball")

    # Attacking actions
    SHOT = "shot", _("Shot")
    GOAL = "goal", _("Goal")
    OWN_GOAL = "own_goal", _("Own goal")
    CHANCE_CREATED = "chance_created", _("Chance created")
    ASSIST = "assist", _("Assist")
    KEY_PASS = "key_pass", _("Key pass")

    # Defensive actions
    TACKLE = "tackle", _("Tackle")
    INTERCEPTION = "interception", _("Interception")
    CLEARANCE = "clearance", _("Clearance")
    BLOCK = "block", _("Block")
    RECOVERY = "recovery", _("Recovery")
    AERIAL_DUEL = "aerial_duel", _("Aerial duel")
    GROUND_DUEL = "ground_duel", _("Ground duel")

    # Goalkeeping
    SAVE = "save", _("Save")
    CLAIM = "claim", _("Claim")
    PUNCH = "punch", _("Punch")
    SWEEP = "sweep", _("Sweep")
    DISTRIBUTION = "distribution", _("Distribution")

    # Discipline / stoppages
    FOUL_COMMITTED = "foul_committed", _("Foul committed")
    FOUL_WON = "foul_won", _("Foul won")
    OFFSIDE = "offside", _("Offside")
    YELLOW_CARD = "yellow_card", _("Yellow card")
    RED_CARD = "red_card", _("Red card")
    SECOND_YELLOW_RED = "second_yellow_red", _("Second yellow then red")
    SUBSTITUTION = "substitution", _("Substitution")

    # Restarts
    CORNER_TAKEN = "corner_taken", _("Corner taken")


class EventParticipantRole(models.TextChoices):
    """
    Role played by a participant within a given event.

    This gives us a flexible participant model instead of hardcoding
    fields like player, assister, goalkeeper, fouled_player, etc.
    """
    ACTOR = "actor", _("Actor")
    RECIPIENT = "recipient", _("Recipient")
    TARGET = "target", _("Target")
    ASSISTER = "assister", _("Assister")
    GOALKEEPER = "goalkeeper", _("Goalkeeper")
    WINNER = "winner", _("Winner")
    LOSER = "loser", _("Loser")
    FOULER = "fouler", _("Fouler")
    FOULED = "fouled", _("Fouled")
    CARD_RECEIVER = "card_receiver", _("Card receiver")
    SUBBED_ON = "subbed_on", _("Subbed on")
    SUBBED_OFF = "subbed_off", _("Subbed off")


class EventQualifierValueType(models.TextChoices):
    """
    Type discriminator for qualifier values.

    A qualifier is a typed key/value pair attached to an event.
    Example:
    - key='body_part', value_type='text', text_value='left_foot'
    - key='shot_on_target', value_type='bool', bool_value=True
    """
    TEXT = "text", _("Text")
    INT = "int", _("Integer")
    DECIMAL = "decimal", _("Decimal")
    BOOL = "bool", _("Boolean")
    TEAM = "team", _("Team")
    PLAYER = "player", _("Player")
    EVENT = "event", _("Event")


class EventLinkType(models.TextChoices):
    """
    Relationship type between two events.

    This lets us explicitly model event chains such as:
    - key pass -> resulted in -> shot
    - shot -> resulted in -> goal
    - foul committed -> resulted in -> yellow card
    """
    CAUSED_BY = "caused_by", _("Caused by")
    RESULTED_IN = "resulted_in", _("Resulted in")
    ASSISTED_BY = "assisted_by", _("Assisted by")
    PRECEDED_BY = "preceded_by", _("Preceded by")
    FOLLOWED_BY = "followed_by", _("Followed by")
    RELATED = "related", _("Related")


class MatchEvent(models.Model):
    """
    Core timeline event for a specific match.

    This model is intentionally lean. It stores:
    - which match the event belongs to
    - which team the event is attributed to
    - what happened
    - when it happened
    - where it happened on the pitch
    - a broad success/failure/neutral outcome

    More detailed context is stored in:
    - MatchEventParticipant
    - MatchEventQualifier
    - MatchEventLink
    """

    # The match this event belongs to.
    match = models.ForeignKey(
        MATCH_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
    )

    # The team this event is attributed to.
    # This is useful for deriving team stats later.
    team = models.ForeignKey(
        TEAM_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="match_events",
        help_text=_("Team the event is attributed to for stat derivation."),
    )

    # The top-level event category.
    # Temporarily nullable for the schema transition migration.
    # We will tighten this later once the old rows have been migrated or cleaned.
    event_type = models.CharField(
        max_length=32,
        choices=EventType.choices,
        null=True,
        blank=True,
    )

    # Which phase of the match the event occurred in.
    # Temporarily nullable for the schema transition migration.
    period = models.CharField(
        max_length=4,
        choices=EventPeriod.choices,
        null=True,
        blank=True,
    )

    # Example:
    # 90+3 would be stored as minute=90 and added_minute=3
    minute = models.PositiveSmallIntegerField(default=0)
    added_minute = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("For 90+3, store minute=90 and added_minute=3."),
    )

    # Second within the minute for finer ordering.
    second = models.PositiveSmallIntegerField(default=0)

    # Tie-break ordering when multiple events share the same timestamp.
    # Example: two events both logged at 67:15.
    # Temporarily nullable for the schema transition migration.
    sequence_index = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Tie-break ordering when multiple events share the same timestamp."),
    )

    # Broad outcome flag.
    outcome = models.CharField(
        max_length=16,
        choices=EventOutcome.choices,
        default=EventOutcome.NEUTRAL,
    )

    # Pitch coordinates as percentages from 0 to 100.
    # These are optional for now and can later be filled via a pitch widget in admin.
    start_x = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    start_y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    end_x = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    end_y = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Free-text notes for admins.
    notes = models.TextField(blank=True)

    # Audit timestamps.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Default ordering for event timelines.
        ordering = (
            "match_id",
            "period",
            "minute",
            "added_minute",
            "second",
            "sequence_index",
            "id",
        )
        indexes = [
            # Optimises timeline/event ordering queries within a match.
            models.Index(
                fields=["match", "period", "minute", "added_minute", "second", "sequence_index"],
                name="event_match_time_idx",
            ),
            # Optimises lookups like "all shots in this match".
            models.Index(
                fields=["match", "event_type"],
                name="event_match_type_idx",
            ),
            # Optimises team-based event queries within a match.
            models.Index(
                fields=["match", "team"],
                name="event_match_team_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_event_type_display()} | "
            f"match={self.match_id} | "
            f"{self.minute}+{self.added_minute}:{self.second:02d}"
        )

    def clean(self):
        """
        Model validation for event timing, team consistency, and pitch coordinates.
        """
        errors = {}

        # If a team is supplied, it must match the team attached to the parent match.
        # This keeps event data scoped to the correct club side.
        if self.team_id and self.match_id and self.team_id != self.match.team_id:
            errors["team"] = _("Selected team must match the team attached to the match.")

        # Seconds must be in normal clock range.
        if self.second > 59:
            errors["second"] = _("Second must be between 0 and 59.")

        # If one coordinate in a pair is supplied, the other must be too.
        # Also ensure values stay within the 0..100 pitch percentage range.
        self._validate_point_pair("start_x", "start_y", errors)
        self._validate_point_pair("end_x", "end_y", errors)

        if errors:
            raise ValidationError(errors)

    def _validate_point_pair(self, x_field, y_field, errors):
        """
        Validate an x/y coordinate pair.

        Rules:
        - x and y must either both be present or both be blank
        - if present, each must be between 0 and 100
        """
        x_value = getattr(self, x_field)
        y_value = getattr(self, y_field)

        if (x_value is None) != (y_value is None):
            errors[x_field] = _("X and Y must either both be set or both be blank.")
            errors[y_field] = _("X and Y must either both be set or both be blank.")
            return

        if x_value is not None and not (0 <= float(x_value) <= 100):
            errors[x_field] = _("Coordinate must be between 0 and 100.")
        if y_value is not None and not (0 <= float(y_value) <= 100):
            errors[y_field] = _("Coordinate must be between 0 and 100.")

    def save(self, *args, **kwargs):
        """
        Run full model validation before saving the event.
        """
        self.full_clean()
        super().save(*args, **kwargs)


class MatchEventParticipant(models.Model):
    """
    Flexible participant model for an event.

    This replaces rigid event fields such as:
    - player
    - assister
    - goalkeeper
    - fouled_player
    - substituted_on / substituted_off

    Instead, each participant gets a role.
    """

    # The event this participant belongs to.
    event = models.ForeignKey(
        MatchEvent,
        on_delete=models.CASCADE,
        related_name="participants",
    )

    # The participant's role in the event.
    role = models.CharField(
        max_length=32,
        choices=EventParticipantRole.choices,
    )

    # Optional linked team and player.
    # team can be useful even when player is not linked.
    team = models.ForeignKey(
        TEAM_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    player = models.ForeignKey(
        PLAYER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_participations",
    )

    # Fallback display name when a participant is not linked to a Player row.
    # This is particularly useful for opposition players not yet in the database.
    display_name = models.CharField(
        max_length=120,
        blank=True,
        help_text=_("Use when you want to record a participant without linking a Player row."),
    )

    # Optional shirt number, useful for manual entry and disambiguation.
    shirt_number = models.PositiveSmallIntegerField(null=True, blank=True)

    # Allows more than one participant for the same role on an event.
    sequence_index = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Lets you store more than one participant for the same role."),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("event_id", "role", "sequence_index", "id")
        indexes = [
            # Optimises participant lookups by event and role.
            models.Index(fields=["event", "role"], name="event_part_role_idx"),
            # Optimises reverse queries from a player to all linked event participations.
            models.Index(fields=["player"], name="event_part_player_idx"),
        ]
        constraints = [
            # Prevents duplicate sequence positions for the same role on the same event.
            models.UniqueConstraint(
                fields=["event", "role", "sequence_index"],
                name="uniq_event_part_role_seq",
            )
        ]

    def __str__(self):
        label = self.display_name or (str(self.player) if self.player_id else "Unlinked participant")
        return f"{self.role}: {label}"

    def clean(self):
        """
        Validate that a participant is identifiable and consistent with the event.

        Rules:
        - provide either a linked player or a display name
        - if both team and event.match team are present, they must match
        - if both player and team are present, the player's club must match the team's club
        """
        errors = {}

        # Require at least one way of identifying the participant.
        if not self.player and not self.display_name:
            errors["player"] = _("Provide either a linked player or a display name.")
            errors["display_name"] = _("Provide either a linked player or a display name.")

        # If a participant team is supplied, keep it aligned to the match team.
        # This prevents event participants from being attached to the wrong club team.
        if self.team_id and self.event_id and self.team_id != self.event.match.team_id:
            errors["team"] = _("Selected team must match the team attached to the event's match.")

        # If both a linked player and team are supplied, they must belong to the same club.
        # This is the strongest cross-model validation we can enforce with the current schema.
        if self.player_id and self.team_id and self.player.club_id != self.team.club_id:
            errors["player"] = _("Linked player must belong to the same club as the selected team.")

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Run full model validation before saving the participant.
        """
        self.full_clean()
        super().save(*args, **kwargs)


class MatchEventQualifier(models.Model):
    """
    Typed key/value metadata attached to an event.

    This is where event-specific detail lives without bloating MatchEvent.

    Example qualifier keys you may use later:
    - body_part
    - shot_on_target
    - chance_quality
    - set_piece_type
    - under_pressure
    - scored_for_team
    - card_reason
    - restart_reason
    """

    # The event this qualifier belongs to.
    event = models.ForeignKey(
        MatchEvent,
        on_delete=models.CASCADE,
        related_name="qualifiers",
    )

    # Machine-readable key.
    key = models.SlugField(
        max_length=64,
        help_text=_("Canonical machine-readable key, e.g. body_part or shot_on_target."),
    )

    # Indicates which one of the typed value fields should be populated.
    value_type = models.CharField(
        max_length=16,
        choices=EventQualifierValueType.choices,
    )

    # Exactly one of these typed value fields should be set.
    text_value = models.TextField(blank=True)
    int_value = models.IntegerField(null=True, blank=True)
    decimal_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bool_value = models.BooleanField(null=True, blank=True)
    team_value = models.ForeignKey(
        TEAM_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    player_value = models.ForeignKey(
        PLAYER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    event_value = models.ForeignKey(
        MatchEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    # Allows multiple qualifiers with the same key if needed later.
    sequence_index = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("event_id", "key", "sequence_index", "id")
        indexes = [
            # Optimises qualifier lookups by event and key.
            models.Index(fields=["event", "key"], name="event_qual_key_idx"),
        ]
        constraints = [
            # Prevent duplicate sequence positions for the same key on the same event.
            models.UniqueConstraint(
                fields=["event", "key", "sequence_index"],
                name="uniq_event_qual_key_seq",
            )
        ]

    def __str__(self):
        return f"{self.key} ({self.value_type})"

    @property
    def value(self):
        """
        Convenience accessor that returns the active typed value
        based on value_type.
        """
        mapping = {
            EventQualifierValueType.TEXT: self.text_value,
            EventQualifierValueType.INT: self.int_value,
            EventQualifierValueType.DECIMAL: self.decimal_value,
            EventQualifierValueType.BOOL: self.bool_value,
            EventQualifierValueType.TEAM: self.team_value,
            EventQualifierValueType.PLAYER: self.player_value,
            EventQualifierValueType.EVENT: self.event_value,
        }
        return mapping[self.value_type]

    def clean(self):
        """
        Ensure exactly one typed value field is populated,
        and that it matches value_type.

        Additional consistency rules:
        - team_value must match the team attached to the event's match
        - event_value must belong to the same match as the parent event
        - if both player_value and team_value are supplied, they must belong to the same club
        """
        provided_values = {
            EventQualifierValueType.TEXT: bool(self.text_value),
            EventQualifierValueType.INT: self.int_value is not None,
            EventQualifierValueType.DECIMAL: self.decimal_value is not None,
            EventQualifierValueType.BOOL: self.bool_value is not None,
            EventQualifierValueType.TEAM: self.team_value_id is not None,
            EventQualifierValueType.PLAYER: self.player_value_id is not None,
            EventQualifierValueType.EVENT: self.event_value_id is not None,
        }

        selected_count = sum(provided_values.values())
        errors = {}

        # Exactly one typed value field must be populated.
        if selected_count != 1:
            errors["value_type"] = _(
                "Exactly one typed value field must be populated on a qualifier."
            )

        # The populated value must match value_type.
        elif not provided_values.get(self.value_type, False):
            errors["value_type"] = _("The populated value field must match value_type.")

        # If a team qualifier is used, keep it aligned to the match team.
        if self.team_value_id and self.event_id and self.team_value_id != self.event.match.team_id:
            errors["team_value"] = _(
                "Selected team value must match the team attached to the event's match."
            )

        # If an event qualifier is used, it must reference an event from the same match.
        if self.event_value_id and self.event_id:
            if self.event_value.match_id != self.event.match_id:
                errors["event_value"] = _(
                    "Selected event value must belong to the same match as the parent event."
                )

        # If both player_value and team_value are populated, keep them club-consistent.
        if self.player_value_id and self.team_value_id:
            if self.player_value.club_id != self.team_value.club_id:
                errors["player_value"] = _(
                    "Selected player value must belong to the same club as the selected team value."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Run full model validation before saving the qualifier.
        """
        self.full_clean()
        super().save(*args, **kwargs)


class MatchEventLink(models.Model):
    """
    Explicit relationship between two MatchEvent rows.

    This is useful when event chains matter and should be preserved
    structurally rather than inferred later.
    """

    # Source event in the relationship.
    from_event = models.ForeignKey(
        MatchEvent,
        on_delete=models.CASCADE,
        related_name="outgoing_links",
    )

    # Target event in the relationship.
    to_event = models.ForeignKey(
        MatchEvent,
        on_delete=models.CASCADE,
        related_name="incoming_links",
    )

    # Nature of the relationship between the two events.
    link_type = models.CharField(
        max_length=24,
        choices=EventLinkType.choices,
    )

    # Allows multiple same-type links between the same events if ever needed.
    sequence_index = models.PositiveSmallIntegerField(default=0)

    # Optional admin notes.
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("from_event_id", "sequence_index", "id")
        indexes = [
            # Optimises outgoing link lookups.
            models.Index(fields=["from_event", "link_type"], name="event_link_from_idx"),
            # Optimises incoming link lookups.
            models.Index(fields=["to_event", "link_type"], name="event_link_to_idx"),
        ]
        constraints = [
            # Prevent exact duplicate link rows with the same sequence slot.
            models.UniqueConstraint(
                fields=["from_event", "to_event", "link_type", "sequence_index"],
                name="uniq_event_link_triplet_seq",
            )
        ]

    def __str__(self):
        return f"{self.from_event_id} {self.link_type} {self.to_event_id}"

    def clean(self):
        """
        Validate basic event link integrity.

        Rules:
        - an event cannot link to itself
        - linked events must belong to the same match
        """
        errors = {}

        # Prevent self-linking.
        if self.from_event_id and self.to_event_id and self.from_event_id == self.to_event_id:
            errors["to_event"] = _("An event cannot link to itself.")

        # Linked events must belong to the same match.
        if self.from_event_id and self.to_event_id:
            if self.from_event.match_id != self.to_event.match_id:
                errors["to_event"] = _("Linked events must belong to the same match.")

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Run full model validation before saving the event link.
        """
        self.full_clean()
        super().save(*args, **kwargs)
