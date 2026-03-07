"""
Models for the standings app.

This file stores league table and ladder data for a team within a
competition and season. These records can be entered manually by an
admin or later recalculated from match results if desired.
"""

from django.db import models
from django.core.exceptions import ValidationError
from competitions.models import Competition
from seasons.models import Season
from teams.models import Team


class Standing(models.Model):
    """Store a team's standing in a competition for a specific season."""

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="standings",
        help_text="The team that this standing record belongs to.",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="standings",
        help_text="The season that this standing record belongs to.",
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="standings",
        help_text="The competition that this standing record belongs to.",
    )
    position = models.PositiveIntegerField(
        help_text="Current ladder position of the team.",
    )
    played = models.PositiveIntegerField(
        default=0,
        help_text="Number of matches played.",
    )
    won = models.PositiveIntegerField(
        default=0,
        help_text="Number of matches won.",
    )
    drawn = models.PositiveIntegerField(
        default=0,
        help_text="Number of matches drawn.",
    )
    lost = models.PositiveIntegerField(
        default=0,
        help_text="Number of matches lost.",
    )
    goals_for = models.PositiveIntegerField(
        default=0,
        help_text="Total goals scored by the team.",
    )
    goals_against = models.PositiveIntegerField(
        default=0,
        help_text="Total goals conceded by the team.",
    )
    goal_difference = models.IntegerField(
        default=0,
        help_text="Goal difference, typically goals for minus goals against.",
    )
    points = models.PositiveIntegerField(
        default=0,
        help_text="Total competition points.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this standing record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this standing record was last updated.",
    )

    class Meta:
        ordering = ["season__name", "competition__name", "position", "team__name"]
        verbose_name = "Standing"
        verbose_name_plural = "Standings"
        constraints = [
            models.UniqueConstraint(
                fields=["team", "season", "competition"],
                name="unique_team_standing_per_season_competition",
            ),
            models.UniqueConstraint(
                fields=["season", "competition", "position"],
                name="unique_position_per_season_competition",
            ),
        ]

    def clean(self):
        """Validate that team, season, and competition belong to the same club."""
        errors = {}

        team_club_id = self.team.club_id if self.team_id else None
        season_club_id = self.season.club_id if self.season_id else None
        competition_club_id = self.competition.club_id if self.competition_id else None

        if team_club_id and season_club_id and team_club_id != season_club_id:
            errors["season"] = "Selected season must belong to the same club as the team."

        if team_club_id and competition_club_id and team_club_id != competition_club_id:
            errors["competition"] = "Selected competition must belong to the same club as the team."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full model validation before saving the standing."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.team} | {self.competition} | Position {self.position}"
