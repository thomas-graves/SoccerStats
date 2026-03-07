"""
Models for the matches app.

This file stores fixture and match-level data.
A match ties together a team, season, competition, venue, opponent,
and basic result information.
"""

from django.core.exceptions import ValidationError
from django.db import models

from competitions.models import Competition
from opponents.models import OpponentTeam
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


class MatchResolutionChoices(models.TextChoices):
    """Define how the final result of the match was resolved."""

    REGULAR_TIME = "regular_time", "Regular time"
    DRAW = "draw", "Draw"
    EXTRA_TIME = "extra_time", "Extra time"
    PENALTIES = "penalties", "Penalties"


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
    opponent = models.ForeignKey(
        OpponentTeam,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matches",
        help_text="The opposing team.",
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
    match_length_minutes = models.PositiveIntegerField(
        default=90,
        help_text="Total scheduled match length in minutes.",
    )
    half_length_minutes = models.PositiveIntegerField(
        default=45,
        help_text="Scheduled length of each half in minutes.",
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
        help_text="The number of goals scored by the club team in normal or extra time.",
    )
    opponent_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="The number of goals scored by the opposing team in normal or extra time.",
    )
    result_resolution = models.CharField(
        max_length=20,
        choices=MatchResolutionChoices.choices,
        blank=True,
        null=True,
        help_text="How the final result of the match was resolved.",
    )
    penalties_team_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Penalty shootout goals scored by the club team, if applicable.",
    )
    penalties_opponent_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Penalty shootout goals scored by the opponent, if applicable.",
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
        ordering = ["-match_date", "kickoff_time", "team__name", "opponent__name"]
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

        if self.status == MatchStatusChoices.PLAYED:
            if self.team_score is None or self.opponent_score is None:
                errors["team_score"] = "Played matches must include both team and opponent scores."

        if self.result_resolution == MatchResolutionChoices.PENALTIES:
            if self.penalties_team_score is None or self.penalties_opponent_score is None:
                errors["penalties_team_score"] = "Penalty shootout scores are required when the match was decided on penalties."

        if self.result_resolution != MatchResolutionChoices.PENALTIES:
            if self.penalties_team_score is not None or self.penalties_opponent_score is not None:
                errors["result_resolution"] = "Penalty shootout scores should only be entered when the result was decided on penalties."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full model validation before saving the match."""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def outcome(self):
        """Return the club team's outcome based on the recorded scoreline."""
        if self.team_score is None or self.opponent_score is None:
            return ""

        if self.team_score > self.opponent_score:
            return "Win"
        if self.team_score < self.opponent_score:
            return "Loss"
        return "Draw"

    def __str__(self):
        """Return the most human-friendly string representation."""
        opponent_name = self.opponent.name if self.opponent else "Unknown opponent"
        return f"{self.team} vs {opponent_name} ({self.match_date})"
