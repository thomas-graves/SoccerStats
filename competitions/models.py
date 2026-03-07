"""
Models for the competitions app.

This file stores competition-level data such as leagues, cups,
and other organised tournaments that teams participate in.
"""

from django.db import models

from clubs.models import Club


class Competition(models.Model):
    """Store the basic details for a competition associated with a club."""

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="competitions",
        help_text="The club that manages or tracks this competition.",
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
    
    