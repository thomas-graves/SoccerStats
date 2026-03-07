"""
Models for the events app.

This file stores match event data such as goals, cards, and substitutions.
Each event belongs to a specific match and can optionally be linked to one
or two lineup entries, depending on the event type.
"""

from django.db import models

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

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.match} | {self.event_type} | {self.minute}'"
