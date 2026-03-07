"""
Models for the competitions app.

This file stores competition-level data such as leagues, cups,
and friendly matches that teams participate in.
Competitions remain scoped to a club for internal management,
but can also be linked to an external organising association.
"""

from django.db import models

from associations.models import Association
from clubs.models import Club


class CompetitionTypeChoices(models.TextChoices):
    """Define the supported competition formats."""

    LEAGUE = "league", "League"
    CUP = "cup", "Cup"
    FRIENDLY = "friendly", "Friendly"
    PRESEASON_FRIENDLY = "preseason_friendly", "Pre-season friendly"


class Competition(models.Model):
    """Store the basic details for a competition associated with a club."""

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="competitions",
        help_text="The club that tracks this competition in the app.",
    )
    association = models.ForeignKey(
        Association,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="competitions",
        help_text="The external association or organising body that manages this competition.",
    )
    name = models.CharField(
        max_length=100,
        help_text="Full competition name used throughout the site.",
    )
    short_name = models.CharField(
        max_length=30,
        blank=True,
        help_text="Optional shorter competition name for compact displays.",
    )
    slug = models.SlugField(
        max_length=120,
        help_text="URL-friendly identifier for the competition.",
    )
    competition_type = models.CharField(
        max_length=30,
        choices=CompetitionTypeChoices.choices,
        default=CompetitionTypeChoices.LEAGUE,
        help_text="The format or type of competition.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this competition record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this competition record was last updated.",
    )

    class Meta:
        ordering = ["club__name", "name"]
        verbose_name = "Competition"
        verbose_name_plural = "Competitions"
        constraints = [
            models.UniqueConstraint(
                fields=["club", "name"],
                name="unique_competition_name_per_club",
            ),
            models.UniqueConstraint(
                fields=["club", "slug"],
                name="unique_competition_slug_per_club",
            ),
        ]

    def __str__(self):
        """Return the most human-friendly string representation."""
        return self.short_name or self.name

