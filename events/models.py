"""
Models for the events app.

This file stores match event data such as goals, cards, and substitutions.
Each event belongs to a specific match and can optionally be linked to one
or two lineup entries, depending on the event type.
"""

from django.db import models
from django.core.exceptions import ValidationError
from coaches.models import MatchCoachAssignment
from lineups.models import LineupEntry
from matches.models import Match


class EventTypeChoices(models.TextChoices):
    """Define the supported types of match events."""

    GOAL = "goal", "Goal"
    OWN_GOAL = "own_goal", "Own goal"
    YELLOW_CARD = "yellow_card", "Yellow card"
    RED_CARD = "red_card", "Red card"
    SUBSTITUTION = "substitution", "Substitution"


class EventSideChoices(models.TextChoices):
    """Define whether the event belongs to the club side or the opponent."""

    CLUB = "club", "Club"
    OPPONENT = "opponent", "Opponent"


class MatchEvent(models.Model):
    """Store a single event that occurred during a match."""

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="events",
        help_text="The match that this event belongs to.",
    )
    event_type = models.CharField(
        max_length=20,
        choices=EventTypeChoices.choices,
        help_text="The type of event recorded for the match.",
    )
    side = models.CharField(
        max_length=10,
        choices=EventSideChoices.choices,
        default=EventSideChoices.CLUB,
        help_text="Whether the event belongs to the club side or the opponent.",
    )
    minute = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="The minute the event occurred in normal time.",
    )
    stoppage_minute = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Optional stoppage time minute added to the main match minute.",
    )
    lineup_entry = models.ForeignKey(
        LineupEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_events",
        help_text="The main lineup entry linked to this event, if applicable.",
    )
    related_lineup_entry = models.ForeignKey(
        LineupEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="secondary_events",
        help_text="An optional second lineup entry, mainly for substitutions.",
    )
    match_coach_assignment = models.ForeignKey(
        MatchCoachAssignment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        help_text="Optional match coach assignment linked to this event, mainly for coach cards.",
    )
    opponent_player_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional opponent player name when no lineup entry exists.",
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional notes providing extra context for the event.",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order for events recorded at the same minute.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this event record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this event record was last updated.",
    )

    class Meta:
        ordering = ["match__match_date", "minute", "stoppage_minute", "sort_order", "id"]
        verbose_name = "Match event"
        verbose_name_plural = "Match events"

    def clean(self):
        """Validate that linked lineup or coach records belong to the same match."""
        errors = {}

        primary_match_id = self.lineup_entry.match_id if self.lineup_entry_id and self.lineup_entry else None
        secondary_match_id = (
            self.related_lineup_entry.match_id
            if self.related_lineup_entry_id and self.related_lineup_entry
            else None
        )
        coach_match_id = (
            self.match_coach_assignment.match_id
            if self.match_coach_assignment_id and self.match_coach_assignment
            else None
        )

        if self.match_id and primary_match_id and self.match_id != primary_match_id:
            errors["lineup_entry"] = "Selected lineup entry must belong to the same match."

        if self.match_id and secondary_match_id and self.match_id != secondary_match_id:
            errors["related_lineup_entry"] = (
                "Selected related lineup entry must belong to the same match."
            )

        if self.match_id and coach_match_id and self.match_id != coach_match_id:
            errors["match_coach_assignment"] = (
                "Selected match coach assignment must belong to the same match."
            )

        if self.event_type != EventTypeChoices.SUBSTITUTION and self.related_lineup_entry_id:
            errors["related_lineup_entry"] = (
                "A related lineup entry should only be used for substitutions."
            )

        if self.match_coach_assignment_id and self.event_type not in {
            EventTypeChoices.YELLOW_CARD,
            EventTypeChoices.RED_CARD,
        }:
            errors["match_coach_assignment"] = (
                "A match coach assignment should only be used for yellow or red card events."
            )

        if self.match_coach_assignment_id and (
            self.lineup_entry_id or self.related_lineup_entry_id
        ):
            errors["match_coach_assignment"] = (
                "Coach card events should use a match coach assignment instead of lineup entries."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full model validation before saving the event."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.match} | {self.event_type} | {self.minute}'"
