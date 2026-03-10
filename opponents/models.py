"""
Models for the opponents app.

This file stores external opponent teams that the club can play against.
Using a dedicated opponent model helps keep opponent names consistent
across fixtures, results, and head-to-head history.
"""

from django.core.exceptions import ValidationError
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


class OpponentLineupEntry(models.Model):
    """
    Store an opponent participant for a specific match.

    This gives the event system a match-context record for opponent-side
    players similar to how LineupEntry works for the club side, while still
    allowing incomplete data.

    In practice this supports:
    - named opponent players
    - shirt-number-only opponent players
    - unknown opponents such as "Unknown #0"
    """

    match = models.ForeignKey(
        "matches.Match",
        on_delete=models.CASCADE,
        related_name="opponent_lineup_entries",
        help_text="The match this opponent lineup entry belongs to.",
    )
    opponent_team = models.ForeignKey(
        OpponentTeam,
        on_delete=models.CASCADE,
        related_name="lineup_entries",
        help_text="The opponent team this lineup entry belongs to.",
    )
    display_name = models.CharField(
        max_length=120,
        blank=True,
        help_text=(
            "Opponent player name for this match. "
            "Leave blank only if shirt number alone is being used."
        ),
    )
    shirt_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Optional opponent shirt number for this match.",
    )
    is_starter = models.BooleanField(
        default=True,
        help_text="Whether this opponent participant started the match.",
    )
    is_known = models.BooleanField(
        default=True,
        help_text=(
            "Use False for placeholder entries such as 'Unknown #0' when the "
            "exact opponent player identity is not known."
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this opponent lineup entry was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this opponent lineup entry was last updated.",
    )

    class Meta:
        ordering = ("match_id", "opponent_team__name", "shirt_number", "display_name", "id")
        verbose_name = "Opponent lineup entry"
        verbose_name_plural = "Opponent lineup entries"
        constraints = [
            models.UniqueConstraint(
                fields=["match", "opponent_team", "shirt_number"],
                condition=models.Q(shirt_number__isnull=False),
                name="uniq_opponent_lineup_shirt_per_match",
            ),
        ]
        indexes = [
            models.Index(
                fields=["match", "opponent_team"],
                name="opp_lineup_match_team_idx",
            ),
            models.Index(
                fields=["match", "shirt_number"],
                name="opp_lineup_match_shirt_idx",
            ),
        ]

    def __str__(self):
        """
        Return the most useful label for admin and event entry.
        """
        if self.display_name and self.shirt_number is not None:
            return f"{self.display_name} #{self.shirt_number}"
        if self.display_name:
            return self.display_name
        if self.shirt_number is not None:
            return f"Unknown #{self.shirt_number}"
        return "Unknown opponent"

    def clean(self):
        """
        Validate that the opponent lineup entry matches the match opponent.

        Rules:
        - the selected opponent team must match match.opponent
        - at least one identifier should be present:
          display_name or shirt_number
        """
        errors = {}

        if self.match_id and self.opponent_team_id:
            if self.match.opponent_id != self.opponent_team_id:
                errors["opponent_team"] = (
                    "Selected opponent team must match the opponent attached to the match."
                )

        if not self.display_name and self.shirt_number is None:
            errors["display_name"] = (
                "Provide at least a display name or a shirt number for the opponent participant."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Run full model validation before saving the opponent lineup entry.
        """
        self.full_clean()
        super().save(*args, **kwargs)