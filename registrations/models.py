"""
Models for the registrations app.

This file links players to teams for a specific season.
These records will later support squad lists, lineups, appearances,
and season-based player statistics.
"""

from django.db import models

from players.models import Player
from seasons.models import Season
from teams.models import Team


class PlayerRegistration(models.Model):
    """Link a player to a team for a specific season."""

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="registrations",
        help_text="The player being registered.",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="registrations",
        help_text="The team the player is registered to.",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="registrations",
        help_text="The season the registration applies to.",
    )
    squad_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Optional squad number for the player in this team and season.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether this registration is currently active.",
    )
    joined_on = models.DateField(
        blank=True,
        null=True,
        help_text="Optional date the player joined the team for this season.",
    )
    left_on = models.DateField(
        blank=True,
        null=True,
        help_text="Optional date the player left the team for this season.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this registration record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this registration record was last updated.",
    )

    class Meta:
        ordering = ["season__name", "team__name", "player__last_name", "player__first_name"]
        verbose_name = "Player registration"
        verbose_name_plural = "Player registrations"
        constraints = [
            models.UniqueConstraint(
                fields=["player", "team", "season"],
                name="unique_player_team_season_registration",
            ),
        ]

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.player} | {self.team} | {self.season}"
