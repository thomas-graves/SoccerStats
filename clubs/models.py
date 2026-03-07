"""
Models for the clubs app.

This file stores organisation-level data.
The Club model is the top-level entity for the soccer stats project.
"""

from django.db import models


class Club(models.Model):
    """Store the basic details for a soccer club."""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Full club name used throughout the site.",
    )
    short_name = models.CharField(
        max_length=30,
        blank=True,
        help_text="Optional shorter club name for compact displays.",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        help_text="URL-friendly identifier for the club.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this club record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this club record was last updated.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Club"
        verbose_name_plural = "Clubs"

    def __str__(self):
        """Return the most human-friendly string representation."""
        return self.short_name or self.name
    
    