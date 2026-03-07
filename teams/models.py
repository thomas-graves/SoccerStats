"""
Models for the teams app.

This file stores team-level data for the club.
Each team belongs to a club and can later be linked to players,
fixtures, results, and league tables.
"""

from django.db import models

from clubs.models import Club


class Team(models.Model):
    """Store the basic details for a team within a club."""

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="teams",
        help_text="The club that this team belongs to.",
    )
    name = models.CharField(
        max_length=100,
        help_text="Full team name used throughout the site.",
    )
    short_name = models.CharField(
        max_length=30,
        blank=True,
        help_text="Optional shorter team name for compact displays.",
    )
    slug = models.SlugField(
        max_length=120,
        help_text="URL-friendly identifier for the team.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this team record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this team record was last updated.",
    )

    class Meta:
        ordering = ["club__name", "name"]
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        constraints = [
            models.UniqueConstraint(
                fields=["club", "name"],
                name="unique_team_name_per_club",
            ),
            models.UniqueConstraint(
                fields=["club", "slug"],
                name="unique_team_slug_per_club",
            ),
        ]

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.club}: {self.short_name or self.name}"

