"""
Admin configuration for the events app.

This file controls how match event records appear in Django admin.
"""

from django.contrib import admin

from .models import MatchEvent


@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    """Configure how the MatchEvent model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "match",
        "event_type",
        "side",
        "minute",
        "stoppage_minute",
        "lineup_entry",
        "related_lineup_entry",
        "sort_order",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "match__opponent__name",
        "match__team__name",
        "lineup_entry__registration__player__first_name",
        "lineup_entry__registration__player__last_name",
        "related_lineup_entry__registration__player__first_name",
        "related_lineup_entry__registration__player__last_name",
        "opponent_player_name",
        "notes",
    )

    # Filters shown in the admin sidebar.
    list_filter = (
        "event_type",
        "side",
        "match__season",
        "match__competition",
        "match__team",
    )

    # Default ordering for the admin list page.
    ordering = (
        "-match__match_date",
        "minute",
        "stoppage_minute",
        "sort_order",
    )
