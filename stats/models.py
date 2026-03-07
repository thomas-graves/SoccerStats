"""
Models for the stats app.

This file stores structured player match statistics.
These stats sit alongside match events and allow match-by-match
performance data to be recorded in a consistent way.
"""

from django.db import models

from lineups.models import LineupEntry
from matches.models import Match


class PlayerMatchStat(models.Model):
    """Store an individual player's statistics for a specific match."""

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="player_stats",
        help_text="The match that these statistics belong to.",
    )
    lineup_entry = models.ForeignKey(
        LineupEntry,
        on_delete=models.CASCADE,
        related_name="stats",
        help_text="The lineup entry that these statistics belong to.",
    )
    minutes_played = models.PositiveIntegerField(
        default=0,
        help_text="Number of minutes played by the player in the match.",
    )
    goals = models.PositiveIntegerField(
        default=0,
        help_text="Number of goals scored by the player.",
    )
    assists = models.PositiveIntegerField(
        default=0,
        help_text="Number of assists recorded by the player.",
    )
    yellow_cards = models.PositiveIntegerField(
        default=0,
        help_text="Number of yellow cards received by the player.",
    )
    red_cards = models.PositiveIntegerField(
        default=0,
        help_text="Number of red cards received by the player.",
    )
    clean_sheet = models.BooleanField(
        default=False,
        help_text="Whether the player was part of a clean sheet.",
    )
    goals_conceded = models.PositiveIntegerField(
        default=0,
        help_text="Number of goals conceded while the player was on the field.",
    )
    saves = models.PositiveIntegerField(
        default=0,
        help_text="Number of saves made by the player, mainly for goalkeepers.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this stat record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this stat record was last updated.",
    )

    class Meta:
        ordering = [
            "match__match_date",
            "lineup_entry__registration__player__last_name",
            "lineup_entry__registration__player__first_name",
        ]
        verbose_name = "Player match stat"
        verbose_name_plural = "Player match stats"
        constraints = [
            models.UniqueConstraint(
                fields=["match", "lineup_entry"],
                name="unique_player_stat_per_match_lineup",
            ),
        ]

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.match} | {self.lineup_entry.registration.player}"
