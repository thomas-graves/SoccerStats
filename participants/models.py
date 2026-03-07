"""
Models for the participants app.

This file stores competition participants for a given season.
A participant can represent either one of the club's own teams or an
external opponent team, which allows full competition tables to be modelled.
"""

from django.core.exceptions import ValidationError
from django.db import models

from competitions.models import Competition
from opponents.models import OpponentTeam
from seasons.models import Season
from teams.models import Team


class CompetitionParticipant(models.Model):
    """Store a single participant in a competition for a specific season."""

    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="participants",
        help_text="The season this participant belongs to.",
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="participants",
        help_text="The competition this participant belongs to.",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="competition_participants",
        help_text="The club team participating in this competition, if applicable.",
    )
    opponent_team = models.ForeignKey(
        OpponentTeam,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="competition_participants",
        help_text="The external opponent team participating in this competition, if applicable.",
    )
    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional custom display name for the participant in this competition.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether this participant is currently active in the competition.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this participant record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this participant record was last updated.",
    )

    class Meta:
        ordering = ["season__name", "competition__name", "display_name", "id"]
        verbose_name = "Competition participant"
        verbose_name_plural = "Competition participants"
        constraints = [
            models.UniqueConstraint(
                fields=["season", "competition", "team"],
                name="unique_team_participant_per_season_competition",
            ),
            models.UniqueConstraint(
                fields=["season", "competition", "opponent_team"],
                name="unique_opponent_participant_per_season_competition",
            ),
        ]

    def clean(self):
        """Validate that the participant links are internally consistent."""
        errors = {}

        season_club_id = self.season.club_id if self.season_id else None
        competition_club_id = self.competition.club_id if self.competition_id else None
        team_club_id = self.team.club_id if self.team_id else None

        if not self.team_id and not self.opponent_team_id:
            errors["team"] = "A participant must have either a club team or an opponent team."

        if self.team_id and self.opponent_team_id:
            errors["team"] = "A participant cannot have both a club team and an opponent team."

        if season_club_id and competition_club_id and season_club_id != competition_club_id:
            errors["competition"] = "Selected competition must belong to the same club as the season."

        if team_club_id and season_club_id and team_club_id != season_club_id:
            errors["team"] = "Selected team must belong to the same club as the season."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full model validation before saving the participant."""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def name(self):
        """Return the most useful display name for the participant."""
        if self.display_name:
            return self.display_name
        if self.team:
            return self.team.short_name or self.team.name
        if self.opponent_team:
            return self.opponent_team.short_name or self.opponent_team.name
        return "Unknown participant"

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.name} | {self.competition} | {self.season}"
