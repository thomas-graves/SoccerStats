"""
Admin configuration for the matches app.

This file controls how match-related models appear in Django admin.
"""

from django.contrib import admin

from .models import Match


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """Configure how the Match model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "match_date",
        "kickoff_time",
        "team",
        "opponent_name",
        "competition",
        "home_away",
        "status",
        "team_score",
        "opponent_score",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "team__name",
        "opponent_name",
        "competition__name",
        "round_label",
    )

    # Filters shown in the admin sidebar.
    list_filter = (
        "status",
        "home_away",
        "competition",
        "season",
        "team",
    )

    # Default ordering for the admin list page.
    ordering = ("-match_date", "kickoff_time", "team__name")
