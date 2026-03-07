"""
Models for the coaches app.

This file stores coach-level data for the club, links coaches to teams
for specific seasons, and links those registrations to specific matches.
A coach can optionally be linked to a player record when the same person
acts as both a player and a coach in different contexts.
"""

from django.core.exceptions import ValidationError
from django.db import models

from clubs.models import Club
from matches.models import Match
from players.models import Player
from seasons.models import Season
from teams.models import Team


class Coach(models.Model):
    """Store the basic details for a coach associated with a club."""

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="coaches",
        help_text="The club that this coach belongs to.",
    )
    linked_player = models.ForeignKey(
        Player,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coach_profiles",
        help_text="Optional linked player record for someone who is also a player.",
    )
    first_name = models.CharField(
        max_length=50,
        help_text="Coach's first name.",
    )
    last_name = models.CharField(
        max_length=50,
        help_text="Coach's last name.",
    )
    preferred_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional preferred name or nickname for display purposes.",
    )
    slug = models.SlugField(
        max_length=120,
        help_text="URL-friendly identifier for the coach.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether the coach is currently active at the club.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this coach record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this coach record was last updated.",
    )

    class Meta:
        ordering = ["club__name", "last_name", "first_name"]
        verbose_name = "Coach"
        verbose_name_plural = "Coaches"
        constraints = [
            models.UniqueConstraint(
                fields=["club", "slug"],
                name="unique_coach_slug_per_club",
            ),
        ]

    def clean(self):
        """Validate that any linked player belongs to the same club."""
        errors = {}

        linked_player_club_id = self.linked_player.club_id if self.linked_player_id else None
        coach_club_id = self.club_id if self.club_id else None

        if linked_player_club_id and coach_club_id and linked_player_club_id != coach_club_id:
            errors["linked_player"] = "Linked player must belong to the same club as the coach."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full model validation before saving the coach."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the most human-friendly string representation."""
        if self.preferred_name:
            return f"{self.preferred_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


class CoachRegistrationRoleChoices(models.TextChoices):
    """Define the supported coaching roles for a team in a season."""

    HEAD_COACH = "head_coach", "Head coach"
    ASSISTANT_COACH = "assistant_coach", "Assistant coach"
    TEAM_MANAGER = "team_manager", "Team manager"
    GOALKEEPER_COACH = "goalkeeper_coach", "Goalkeeper coach"
    OTHER = "other", "Other"


class CoachRegistration(models.Model):
    """Link a coach to a team for a specific season."""

    coach = models.ForeignKey(
        Coach,
        on_delete=models.CASCADE,
        related_name="registrations",
        help_text="The coach being registered.",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="coach_registrations",
        help_text="The team the coach is registered to.",
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name="coach_registrations",
        help_text="The season the registration applies to.",
    )
    role = models.CharField(
        max_length=30,
        choices=CoachRegistrationRoleChoices.choices,
        default=CoachRegistrationRoleChoices.HEAD_COACH,
        help_text="The coach's primary role for this team and season.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether this registration is currently active.",
    )
    joined_on = models.DateField(
        blank=True,
        null=True,
        help_text="Optional date the coach joined the team for this season.",
    )
    left_on = models.DateField(
        blank=True,
        null=True,
        help_text="Optional date the coach left the team for this season.",
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional notes about the coach's role or arrangement for the season.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this registration record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this registration record was last updated.",
    )

    class Meta:
        ordering = ["season__name", "team__name", "coach__last_name", "coach__first_name"]
        verbose_name = "Coach registration"
        verbose_name_plural = "Coach registrations"
        constraints = [
            models.UniqueConstraint(
                fields=["coach", "team", "season"],
                name="unique_coach_team_season_registration",
            ),
        ]

    def clean(self):
        """Validate that coach, team, and season belong to the same club."""
        errors = {}

        coach_club_id = self.coach.club_id if self.coach_id else None
        team_club_id = self.team.club_id if self.team_id else None
        season_club_id = self.season.club_id if self.season_id else None

        if coach_club_id and team_club_id and coach_club_id != team_club_id:
            errors["team"] = "Selected team must belong to the same club as the coach."

        if coach_club_id and season_club_id and coach_club_id != season_club_id:
            errors["season"] = "Selected season must belong to the same club as the coach."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full model validation before saving the coach registration."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.coach} | {self.team} | {self.season}"


class MatchCoachAssignmentRoleChoices(models.TextChoices):
    """Define the supported matchday coaching roles."""

    HEAD_COACH = "head_coach", "Head coach"
    ASSISTANT_COACH = "assistant_coach", "Assistant coach"
    TEAM_MANAGER = "team_manager", "Team manager"
    GOALKEEPER_COACH = "goalkeeper_coach", "Goalkeeper coach"
    OTHER = "other", "Other"


class MatchCoachAssignment(models.Model):
    """Link a coach registration to a specific match."""

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="coach_assignments",
        help_text="The match this coaching assignment belongs to.",
    )
    coach_registration = models.ForeignKey(
        CoachRegistration,
        on_delete=models.CASCADE,
        related_name="match_assignments",
        help_text="The team-season coach registration assigned to the match.",
    )
    matchday_role = models.CharField(
        max_length=30,
        choices=MatchCoachAssignmentRoleChoices.choices,
        blank=True,
        help_text="Optional matchday-specific role if it differs from the season registration role.",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Display order for showing coaches on the match page.",
    )
    notes = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional notes about this coach's role for the match.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp for when this assignment record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp for when this assignment record was last updated.",
    )

    class Meta:
        ordering = [
            "-match__match_date",
            "display_order",
            "coach_registration__coach__last_name",
            "coach_registration__coach__first_name",
        ]
        verbose_name = "Match coach assignment"
        verbose_name_plural = "Match coach assignments"
        constraints = [
            models.UniqueConstraint(
                fields=["match", "coach_registration"],
                name="unique_coach_registration_per_match",
            ),
        ]

    def clean(self):
        """Validate that the coach registration matches the match team and season."""
        errors = {}

        match_team_id = self.match.team_id if self.match_id else None
        match_season_id = self.match.season_id if self.match_id else None
        registration_team_id = self.coach_registration.team_id if self.coach_registration_id else None
        registration_season_id = (
            self.coach_registration.season_id if self.coach_registration_id else None
        )

        if match_team_id and registration_team_id and match_team_id != registration_team_id:
            errors["coach_registration"] = (
                "Selected coach registration must belong to the same team as the match."
            )

        if match_season_id and registration_season_id and match_season_id != registration_season_id:
            errors["match"] = (
                "Selected coach registration must belong to the same season as the match."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Run full model validation before saving the match coach assignment."""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def effective_role(self):
        """Return the matchday role if present, otherwise fall back to the season role."""
        return self.matchday_role or self.coach_registration.role

    def __str__(self):
        """Return the most human-friendly string representation."""
        return f"{self.match} | {self.coach_registration.coach} | {self.effective_role}"
    
