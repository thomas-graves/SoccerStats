"""
Models for the matches app.

This file stores fixture and match-level data.
A match ties together a team, season, competition, venue, opponent,
and basic result information.
"""

from django.db import models
from django.core.exceptions import ValidationError
from competitions.models import Competition
from seasons.models import Season
from teams.models import Team
from venues.models import Venue


class HomeAwayChoices(models.TextChoices):
    """Define whether the match is home or away."""

    HOME = "home", "Home"
    AWAY = "away", "Away"


class MatchStatusChoices(models.TextChoices):
    """Define the current status of a match."""

    UPCOMING = "upcoming", "Upcoming"
    PLAYED = "played", "Played"
    POSTPONED = "postponed", "Postponed"
    CANCELLED = "cancelled", "Cancelled"
    ABANDONED = "abandoned", "Abandoned"


class Match(models.Model):
    """Store the basic details and result information for a match."""

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="matches",
        help_text="The club team that this match belongs to.",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="matches",
        help_text="The season that this match belongs to.",
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="matches",
        help_text="The competition this match is part of.",
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches",
        help_text="The venue where the match is scheduled to be played.",
    )
    opponent_name = models.CharField(
        max_length=100,
        help_text="The name of the opposing team.",
    )
    home_away = models.CharField(
        max_length=10,
        choices=HomeAwayChoices.choices,
        help_text="Whether the match is home or away.",
    )
    match_date = models.DateField(
        help_text="The scheduled calendar date of the match.",
    )
    kickoff_time = models.TimeField(
        blank=True,
        null=True,
        help_text="The scheduled kickoff time of the match.",
    )
    round_label = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional round label, such as 'Round 1' or 'Semi Final'.",
    )
    status = models.CharField(
        max_length=20,
        choices=MatchStatusChoices.choices,
        default=MatchStatusChoices.UPCOMING,
        help_text="The current status of the match.",
    )
    team_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="The number of goals scored by the club team.",
    )
    opponent_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="The number of goals scored by the opposing team.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this match record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this match record was last updated.",
    )

    class Meta:
        ordering = ["-match_date", "kickoff_time", "team__name", "opponent_name"]
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def clean(self):
        """Validate that linked records belong to a consistent club context."""
        errors = {}

        team_club_id = self.team.club_id if self.team_id else None
        season_club_id = self.season.club_id if self.season_id else None
        competition_club_id = self.competition.club_id if self.competition_id else None
        venue_club_id = self.venue.club_id if self.venue_id and self.venue else None

        if team_club_id and season_club_id and team_club_id != season_club_id:
            errors["season"] = "Selected season must belong to the same club as the team."

        if team_club_id and competition_club_id and team_club_id != competition_club_id:
            errors["competition"] = "Selected competition must belong to the same club as the team."

        if team_club_id and venue_club_id and team_club_id != venue_club_id:
            errors["venue"] = "Selected venue must belong to the same club as the team."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full model validation before saving the match."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.team} vs {self.opponent_name} ({self.match_date})"

