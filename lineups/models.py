"""
Models for the lineups app.

This file stores matchday lineup data.
Each lineup entry links a registered player to a specific match and
captures whether they started or were named on the bench.
"""

from django.db import models
from django.core.exceptions import ValidationError
from matches.models import Match
from registrations.models import PlayerRegistration


class LineupRoleChoices(models.TextChoices):
    """Define whether the player started or was on the bench."""

    STARTER = "starter", "Starter"
    SUBSTITUTE = "substitute", "Substitute"

class PositionLabelChoices(models.TextChoices):
    """Define the supported matchday position labels."""

    GK = "GK", "GK"
    CB = "CB", "CB"
    RB = "RB", "RB"
    LB = "LB", "LB"
    RWB = "RWB", "RWB"
    LWB = "LWB", "LWB"
    CDM = "CDM", "CDM"
    CM = "CM", "CM"
    RM = "RM", "RM"
    LM = "LM", "LM"
    CAM = "CAM", "CAM"
    RW = "RW", "RW"
    LW = "LW", "LW"
    CF = "CF", "CF"
    RS = "RS", "RS"
    LS = "LS", "LS"
    ST = "ST", "ST"

class LineupEntry(models.Model):
    """Store a single player's lineup entry for a specific match."""

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="lineup_entries",
        help_text="The match this lineup entry belongs to.",
    )
    registration = models.ForeignKey(
        PlayerRegistration,
        on_delete=models.CASCADE,
        related_name="lineup_entries",
        help_text="The player registration used for this lineup entry.",
    )
    role = models.CharField(
        max_length=20,
        choices=LineupRoleChoices.choices,
        help_text="Whether the player was named as a starter or substitute.",
    )
    position_label = models.CharField(
        max_length=10,
        choices=PositionLabelChoices.choices,
        blank=True,
        help_text="Optional position label for the player's role in this match.",
    )
    shirt_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Optional shirt number worn by the player for this match.",
    )
    is_captain = models.BooleanField(
        default=False,
        help_text="Indicates whether the player was captain for this match.",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order for the lineup, useful for starters and bench order.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this lineup entry was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this lineup entry was last updated.",
    )

    class Meta:
        ordering = ["match__match_date", "role", "sort_order", "registration__player__last_name"]
        verbose_name = "Lineup entry"
        verbose_name_plural = "Lineup entries"
        constraints = [
            models.UniqueConstraint(
                fields=["match", "registration"],
                name="unique_registration_per_match_lineup",
            ),
        ]

    def clean(self):
        """Validate that the registration matches the match team and season."""
        errors = {}

        match_team_id = self.match.team_id if self.match_id else None
        match_season_id = self.match.season_id if self.match_id else None
        registration_team_id = self.registration.team_id if self.registration_id else None
        registration_season_id = self.registration.season_id if self.registration_id else None

        if match_team_id and registration_team_id and match_team_id != registration_team_id:
            errors["registration"] = "Selected registration must belong to the same team as the match."

        if match_season_id and registration_season_id and match_season_id != registration_season_id:
            errors["match"] = "Selected registration must belong to the same season as the match."

        # Starters must have an initial position so the replay engine can
        # derive the kickoff formation and initial on-pitch position state.
        #
        # Substitutes are allowed to have a blank position here, because their
        # actual entry position can later be captured through the
        # `subbed_on_position` event qualifier when they come onto the pitch.
        if self.role == LineupRoleChoices.STARTER and not self.position_label:
            errors["position_label"] = (
                "Starter lineup entries must include an initial position label."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full model validation before saving the lineup entry."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.match} | {self.registration.player} | {self.role}"

