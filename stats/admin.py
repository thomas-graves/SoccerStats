"""
Admin configuration for the stats app.

This file controls how player match statistics appear in Django admin.
"""

from django.contrib import admin

from .models import PlayerMatchStat


@admin.register(PlayerMatchStat)
class PlayerMatchStatAdmin(admin.ModelAdmin):
    """Configure how the PlayerMatchStat model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "match",
        "lineup_entry",
        "minutes_played",
        "goals",
        "assists",
        "yellow_cards",
        "red_cards",
        "clean_sheet",
        "goals_conceded",
        "saves",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "match__opponent_name",
        "match__team__name",
        "lineup_entry__registration__player__first_name",
        "lineup_entry__registration__player__last_name",
        "lineup_entry__registration__team__name",
    )

    # Filters shown in the admin sidebar.
    list_filter = (
        "match__season",
        "match__competition",
        "match__team",
        "clean_sheet",
    )

    # Default ordering for the admin list page.
    ordering = (
        "-match__match_date",
        "lineup_entry__registration__player__last_name",
        "lineup_entry__registration__player__first_name",
    )
