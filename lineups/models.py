"""
Models for the lineups app.

This file stores matchday lineup data.
Each lineup entry links a registered player to a specific match and
captures whether they started or were named on the bench.
"""

from django.db import models

from matches.models import Match
from registrations.models import PlayerRegistration


class LineupRoleChoices(models.TextChoices):
    """Define whether the player started or was on the bench."""

    STARTER = "starter", "Starter"
    SUBSTITUTE = "substitute", "Substitute"


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
        max_length=30,
        blank=True,
        help_text="Optional position label such as GK, CB, CM, or ST.",
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

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.match} | {self.registration.player} | {self.role}"

