"""
Admin configuration for the standings app.

This file controls how standing records appear in Django admin.
"""

from django.contrib import admin

from .models import Standing


@admin.register(Standing)
class StandingAdmin(admin.ModelAdmin):
    """Configure how the Standing model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "position",
        "participant",
        "played",
        "won",
        "drawn",
        "lost",
        "goals_for",
        "goals_against",
        "goal_difference",
        "points",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "participant__display_name",
        "participant__team__name",
        "participant__opponent_team__name",
        "participant__competition__name",
        "participant__season__name",
    )

    # Filters shown in the admin sidebar.
    list_filter = (
        "participant__season",
        "participant__competition",
    )

    # Default ordering for the admin list page.
    ordering = (
        "participant__season__name",
        "participant__competition__name",
        "position",
    )
