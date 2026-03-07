"""
Models for the venues app.

This file stores venue-level data for match locations.
Venues can later be linked to fixtures, results, and team schedules.
"""

from django.db import models

from clubs.models import Club


class Venue(models.Model):
    """Store the basic details for a venue associated with a club."""

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="venues",
        help_text="The club that manages or tracks this venue.",
    )
    name = models.CharField(
        max_length=100,
        help_text="Full venue name used throughout the site.",
    )
    short_name = models.CharField(
        max_length=30,
        blank=True,
        help_text="Optional shorter venue name for compact displays.",
    )
    slug = models.SlugField(
        max_length=120,
        help_text="URL-friendly identifier for the venue.",
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional street address for the venue.",
    )
    suburb = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional suburb or locality for the venue.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether this venue is currently active.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this venue record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this venue record was last updated.",
    )

    class Meta:
        ordering = ["club__name", "name"]
        verbose_name = "Venue"
        verbose_name_plural = "Venues"
        constraints = [
            models.UniqueConstraint(
                fields=["club", "name"],
                name="unique_venue_name_per_club",
            ),
            models.UniqueConstraint(
                fields=["club", "slug"],
                name="unique_venue_slug_per_club",
            ),
        ]

    def __str__(self):
        """Return the most human-friendly string representation."""
        return self.short_name or self.name
