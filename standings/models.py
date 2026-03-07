"""
Models for the standings app.

This file stores league table and ladder data for a competition participant
within a competition and season. These records can be entered manually by an
admin or later recalculated from match results if desired.
"""

from django.core.exceptions import ValidationError
from django.db import models

from participants.models import CompetitionParticipant


class Standing(models.Model):
    """Store a participant's standing in a competition for a specific season."""

    participant = models.ForeignKey(
        CompetitionParticipant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="standings",
        help_text="The competition participant that this standing record belongs to.",
    )
    position = models.PositiveIntegerField(
        help_text="Current ladder position of the participant.",
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
        help_text="Total goals scored by the participant.",
    )
    goals_against = models.PositiveIntegerField(
        default=0,
        help_text="Total goals conceded by the participant.",
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
        ordering = [
            "participant__season__name",
            "participant__competition__name",
            "position",
            "participant__display_name",
            "participant__id",
        ]
        verbose_name = "Standing"
        verbose_name_plural = "Standings"
        constraints = [
            models.UniqueConstraint(
                fields=["participant"],
                name="unique_standing_per_participant",
            ),
        ]

    def clean(self):
        """Validate that position uniqueness is enforced within a competition table."""
        errors = {}

        if self.participant_id:
            season_id = self.participant.season_id
            competition_id = self.participant.competition_id

            conflicting_qs = Standing.objects.filter(
                participant__season_id=season_id,
                participant__competition_id=competition_id,
                position=self.position,
            )

            if self.pk:
                conflicting_qs = conflicting_qs.exclude(pk=self.pk)

            if conflicting_qs.exists():
                errors["position"] = (
                    "This ladder position is already used in the selected season and competition."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full model validation before saving the standing."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.participant} | Position {self.position}"
    
    