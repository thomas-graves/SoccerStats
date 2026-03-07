"""
Models for the opponents app.

This file stores external opponent teams that the club can play against.
Using a dedicated opponent model helps keep opponent names consistent
across fixtures, results, and head-to-head history.
"""

from django.db import models

from associations.models import Association


class OpponentTeam(models.Model):
    """Store the basic details for an opponent team."""

    association = models.ForeignKey(
        Association,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opponent_teams",
        help_text="Optional association that the opponent team belongs to.",
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Full opponent team name used throughout the site.",
    )
    short_name = models.CharField(
        max_length=30,
        blank=True,
        help_text="Optional shorter opponent team name for compact displays.",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text="URL-friendly identifier for the opponent team.",
    )
    suburb = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional suburb or locality for the opponent team.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether this opponent team is currently active.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this opponent team record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this opponent team record was last updated.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Opponent team"
        verbose_name_plural = "Opponent teams"

    def __str__(self):
        """Return the most human-friendly string representation."""
        return self.short_name or self.name
