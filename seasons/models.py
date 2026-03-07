"""
Models for the seasons app.

This file stores season-level data, such as the 2026 season.
Seasons provide a time-based structure that fixtures, tables,
and statistics can be linked to later.
"""

from django.db import models

from clubs.models import Club


class Season(models.Model):
    """Store the basic details for a season associated with a club."""

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="seasons",
        help_text="The club that this season belongs to.",
    )
    name = models.CharField(
        max_length=50,
        help_text="Display name for the season, such as '2026' or '2025/26'.",
    )
    slug = models.SlugField(
        max_length=60,
        help_text="URL-friendly identifier for the season.",
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Optional start date for the season.",
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Optional end date for the season.",
    )
    is_current = models.BooleanField(
        default=False,
        help_text="Indicates whether this is the club's current active season.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this season record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this season record was last updated.",
    )

    class Meta:
        ordering = ["club__name", "-start_date", "name"]
        verbose_name = "Season"
        verbose_name_plural = "Seasons"
        constraints = [
            models.UniqueConstraint(
                fields=["club", "name"],
                name="unique_season_name_per_club",
            ),
            models.UniqueConstraint(
                fields=["club", "slug"],
                name="unique_season_slug_per_club",
            ),
        ]

    def __str__(self):
        """Return the most human-friendly string representation."""
        return self.name
