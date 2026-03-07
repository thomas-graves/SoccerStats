"""
Admin configuration for the coaches app.

This file controls how coach-related models appear in Django admin.
It includes coach profiles, team-season coach registrations, and
match-specific coach assignments.
"""

from django.contrib import admin

from .models import Coach, CoachRegistration, MatchCoachAssignment


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    """Configure how the Coach model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "first_name",
        "last_name",
        "preferred_name",
        "club",
        "linked_player",
        "is_active",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "first_name",
        "last_name",
        "preferred_name",
        "slug",
        "club__name",
        "linked_player__first_name",
        "linked_player__last_name",
    )

    # Filters shown in the admin sidebar.
    list_filter = ("club", "is_active")

    # Automatically prefill the slug field from the coach's first and last name.
    prepopulated_fields = {"slug": ("first_name", "last_name")}


@admin.register(CoachRegistration)
class CoachRegistrationAdmin(admin.ModelAdmin):
    """Configure how the CoachRegistration model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "coach",
        "team",
        "season",
        "role",
        "is_active",
        "joined_on",
        "left_on",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "coach__first_name",
        "coach__last_name",
        "coach__preferred_name",
        "team__name",
        "season__name",
        "notes",
    )

    # Filters shown in the admin sidebar.
    list_filter = ("season", "team", "role", "is_active")

    # Default ordering for the admin list page.
    ordering = ("season__name", "team__name", "coach__last_name", "coach__first_name")


@admin.register(MatchCoachAssignment)
class MatchCoachAssignmentAdmin(admin.ModelAdmin):
    """Configure how the MatchCoachAssignment model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "match",
        "coach_registration",
        "effective_role",
        "display_order",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "match__team__name",
        "match__opponent__name",
        "coach_registration__coach__first_name",
        "coach_registration__coach__last_name",
        "coach_registration__team__name",
        "coach_registration__season__name",
        "notes",
    )

    # Filters shown in the admin sidebar.
    list_filter = (
        "match__season",
        "match__competition",
        "match__team",
        "coach_registration__role",
        "matchday_role",
    )

    # Default ordering for the admin list page.
    ordering = (
        "-match__match_date",
        "display_order",
        "coach_registration__coach__last_name",
        "coach_registration__coach__first_name",
    )
