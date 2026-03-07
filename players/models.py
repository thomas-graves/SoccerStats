"""
Models for the players app.

This file stores player-level data for the club.
Player records will later be linked to team registrations, lineups,
appearances, match events, and statistics.
"""

from django.db import models

from clubs.models import Club


class Player(models.Model):
    """Store the basic details for a player associated with a club."""

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="players",
        help_text="The club that this player belongs to.",
    )
    first_name = models.CharField(
        max_length=50,
        help_text="Player's first name.",
    )
    last_name = models.CharField(
        max_length=50,
        help_text="Player's last name.",
    )
    preferred_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional preferred name or nickname for display purposes.",
    )
    slug = models.SlugField(
        max_length=120,
        help_text="URL-friendly identifier for the player.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether the player is currently active at the club.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this player record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this player record was last updated.",
    )

    class Meta:
        ordering = ["club__name", "last_name", "first_name"]
        verbose_name = "Player"
        verbose_name_plural = "Players"
        constraints = [
            models.UniqueConstraint(
                fields=["club", "slug"],
                name="unique_player_slug_per_club",
            ),
        ]

    def __str__(self):
        """Return the most human-friendly string representation."""
        if self.preferred_name:
            return f"{self.preferred_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
