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
LINEUP_ENTRY_MODEL = "lineups.LineupEntry"
MATCH_COACH_ASSIGNMENT_MODEL = "coaches.MatchCoachAssignment"


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
    Richer event outcomes used to support stat derivation and clearer event semantics.

    Not every event type will use every outcome, but having a shared controlled
    vocabulary makes downstream logic much simpler.
    """

    COMPLETED = "completed", _("Completed")
    INCOMPLETE = "incomplete", _("Incomplete")
    SUCCESSFUL = "successful", _("Successful")
    UNSUCCESSFUL = "unsuccessful", _("Unsuccessful")
    WON = "won", _("Won")
    LOST = "lost", _("Lost")
    SCORED = "scored", _("Scored")
    SAVED = "saved", _("Saved")
    BLOCKED = "blocked", _("Blocked")
    OFF_TARGET = "off_target", _("Off target")
    NEUTRAL = "neutral", _("Neutral")


class EventTeamSide(models.TextChoices):
    """
    Side attribution for a match event.

    This is needed because events may belong to:
    - the club side
    - the opponent side
    - neither side directly, for neutral control events
    """

    CLUB = "club", _("Club")
    OPPONENT = "opponent", _("Opponent")
    NEUTRAL = "neutral", _("Neutral")


class EventType(models.TextChoices):
    """
    Canonical list of supported core event types.

    These are intentionally the main football actions, not every possible
    subtype or derived concept. More detailed meaning is stored through:
    - qualifiers
    - participants
    - event links
    - derived stats
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
    PASS = "pass", _("Pass")
    CARRY = "carry", _("Carry")
    DRIBBLE = "dribble", _("Dribble")

    # Attacking actions
    SHOT = "shot", _("Shot")
    OWN_GOAL = "own_goal", _("Own goal")

    # Defensive actions
    TACKLE = "tackle", _("Tackle")
    INTERCEPTION = "interception", _("Interception")
    CLEARANCE = "clearance", _("Clearance")
    BLOCK = "block", _("Block")
    BALL_RECOVERY = "ball_recovery", _("Ball recovery")
    AERIAL_DUEL = "aerial_duel", _("Aerial duel")

    # Goalkeeping
    SAVE = "save", _("Save")
    CLAIM = "claim", _("Claim")

    # Discipline / stoppages
    FOUL_COMMITTED = "foul_committed", _("Foul committed")
    FOUL_WON = "foul_won", _("Foul won")
    OFFSIDE = "offside", _("Offside")
    CARD = "card", _("Card")
    SUBSTITUTION = "substitution", _("Substitution")


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


class EventQualifierKey(models.TextChoices):
    """
    Controlled qualifier keys for structured event metadata.

    These keys define the kinds of metadata that can be attached to events
    without bloating the core MatchEvent table.
    """

    # General
    BODY_PART = "body_part", _("Body part")
    UNDER_PRESSURE = "under_pressure", _("Under pressure")
    BIG_CHANCE = "big_chance", _("Big chance")

    # Passing
    PASS_LENGTH = "pass_length", _("Pass length")
    PASS_PROFILE = "pass_profile", _("Pass profile")
    PASS_HEIGHT = "pass_height", _("Pass height")
    PASS_DIRECTION = "pass_direction", _("Pass direction")
    PROGRESSIVE = "progressive", _("Progressive")

    # Restarts / set pieces
    RESTART_TYPE = "restart_type", _("Restart type")
    RESTART_SIDE = "restart_side", _("Restart side")
    FREE_KICK_PROFILE = "free_kick_profile", _("Free kick profile")

    # Shooting
    SHOT_ZONE = "shot_zone", _("Shot zone")
    SHOT_ON_TARGET = "shot_on_target", _("Shot on target")
    SHOT_TARGET_HORIZONTAL = "shot_target_horizontal", _("Shot target horizontal")
    SHOT_TARGET_VERTICAL = "shot_target_vertical", _("Shot target vertical")
    HIT_WOODWORK = "hit_woodwork", _("Hit woodwork")

    # Tackles / fouls / cards
    TACKLE_PROFILE = "tackle_profile", _("Tackle profile")
    FOUL_PROFILE = "foul_profile", _("Foul profile")
    CARD_TYPE = "card_type", _("Card type")
    CARD_REASON = "card_reason", _("Card reason")


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
    - which side the event is attributed to
    - what happened
    - when it happened
    - where it happened on the pitch
    - a broad structured outcome

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

    # Which side the event belongs to.
    #
    # We store side explicitly because match events may belong to:
    # - the club side
    # - the opponent side
    # - neither side directly for neutral control events
    #
    # The club team itself is already available via match.team, so storing
    # an internal Team foreign key here is no longer the right primary marker.
    team_side = models.CharField(
        max_length=10,
        choices=EventTeamSide.choices,
        default=EventTeamSide.CLUB,
        help_text=_("Which side this event is attributed to."),
    )

    # The top-level event category.
    event_type = models.CharField(
        max_length=32,
        choices=EventType.choices,
    )

    # Which phase of the match the event occurred in.
    period = models.CharField(
        max_length=4,
        choices=EventPeriod.choices,
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
    sequence_index = models.PositiveIntegerField(
        default=0,
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
            # Optimises side-based event queries within a match.
            models.Index(
                fields=["match", "team_side"],
                name="event_match_side_idx",
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

    This model stores the people involved in a match event using match-context
    references wherever possible.

    Current participant sources:
    - lineup_entry for club-side players involved in the match
    - match_coach_assignment for coaches involved in the match
    - display_name as a fallback for opponent or unknown participants

    This keeps the event system aligned to the actual match context while still
    allowing incomplete or opponent-side data to be recorded.
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

    # Club-side player reference for this specific match.
    lineup_entry = models.ForeignKey(
        LINEUP_ENTRY_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_participations",
        help_text=_("Use for club-side player participants tied to this specific match."),
    )

    # Coach reference for this specific match.
    match_coach_assignment = models.ForeignKey(
        MATCH_COACH_ASSIGNMENT_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_participations",
        help_text=_("Use for coach participants tied to this specific match."),
    )

    # Fallback display name when the participant is not linked to a club lineup
    # entry or coach assignment. This is particularly useful for:
    # - opponent players
    # - unknown participants such as 'Unknown #0'
    display_name = models.CharField(
        max_length=120,
        blank=True,
        help_text=_(
            "Use when you want to record an opponent or unknown participant "
            "without linking a club-side lineup or coach record."
        ),
    )

    # Optional shirt number, useful for opponent players and unknown participants.
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
            # Optimises reverse queries from a lineup entry to all linked event participations.
            models.Index(fields=["lineup_entry"], name="event_part_lineup_idx"),
            # Optimises reverse queries from a match coach assignment to all linked event participations.
            models.Index(
                fields=["match_coach_assignment"],
                name="event_part_coach_idx",
            ),
        ]
        constraints = [
            # Prevents duplicate sequence positions for the same role on the same event.
            models.UniqueConstraint(
                fields=["event", "role", "sequence_index"],
                name="uniq_event_part_role_seq",
            )
        ]

    def __str__(self):
        """
        Return the most helpful participant label for admin and debugging.
        """
        if self.lineup_entry_id:
            return f"{self.role}: {self.lineup_entry.registration.player}"
        if self.match_coach_assignment_id:
            return f"{self.role}: {self.match_coach_assignment.coach_registration.coach}"
        if self.display_name:
            return f"{self.role}: {self.display_name}"
        return f"{self.role}: Unlinked participant"

    def clean(self):
        """
        Validate that the participant is identifiable and belongs to the same match.

        Rules:
        - exactly one of lineup_entry, match_coach_assignment, or display_name
          should be used as the participant source
        - lineup_entry must belong to the same match as the event
        - match_coach_assignment must belong to the same match as the event
        """
        errors = {}

        source_count = sum(
            [
                bool(self.lineup_entry_id),
                bool(self.match_coach_assignment_id),
                bool(self.display_name),
            ]
        )

        if source_count == 0:
            errors["display_name"] = _(
                "Provide a lineup entry, a match coach assignment, or a display name."
            )

        if source_count > 1:
            errors["display_name"] = _(
                "Use only one participant source: lineup entry, match coach assignment, or display name."
            )

        if self.lineup_entry_id and self.event_id:
            if self.lineup_entry.match_id != self.event.match_id:
                errors["lineup_entry"] = _(
                    "Selected lineup entry must belong to the same match as the event."
                )

        if self.match_coach_assignment_id and self.event_id:
            if self.match_coach_assignment.match_id != self.event.match_id:
                errors["match_coach_assignment"] = _(
                    "Selected match coach assignment must belong to the same match as the event."
                )

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

    # Controlled qualifier key.
    #
    # We use a fixed enum here so qualifiers stay consistent across matches,
    # which is important for reliable stat derivation later.
    key = models.CharField(
        max_length=32,
        choices=EventQualifierKey.choices,
        help_text=_("Controlled qualifier key for this event metadata row."),
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
