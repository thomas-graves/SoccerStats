"""
Models for the associations app.

This file stores external organising bodies such as football associations
or leagues that manage competitions. These records can later be linked to
competitions so the app can distinguish between club-run and association-run
competitions.
"""

from django.db import models


class Association(models.Model):
    """Store the basic details for a competition organising body."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Full association name used throughout the site.",
    )
    short_name = models.CharField(
        max_length=30,
        blank=True,
        help_text="Optional shorter association name for compact displays.",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text="URL-friendly identifier for the association.",
    )
    website_url = models.URLField(
        blank=True,
        help_text="Optional website URL for the association.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether this association is currently active.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this association record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this association record was last updated.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Association"
        verbose_name_plural = "Associations"

    def __str__(self):
        """Return the most human-friendly string representation."""
        return self.short_name or self.name
