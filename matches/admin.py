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
        "opponent",
        "competition",
        "venue",
        "home_away",
        "status",
        "team_score",
        "opponent_score",
        "outcome",
        "event_capture_mode",
        "player_of_the_match",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "team__name",
        "opponent__name",
        "competition__name",
        "round_label",
        "venue__name",
        "player_of_the_match__registration__player__first_name",
        "player_of_the_match__registration__player__last_name",
    )

    # Filters shown in the admin sidebar.
    list_filter = (
        "status",
        "home_away",
        "competition",
        "season",
        "team",
        "result_resolution",
        "event_capture_mode",
    )

    # Default ordering for the admin list page.
    ordering = ("-match_date", "kickoff_time", "team__name")

    # Make related-object selection easier to use.
    autocomplete_fields = ["player_of_the_match"]

    # Group fields into clearer sections in the admin form.
    fieldsets = (
        (
            "Fixture details",
            {
                "fields": (
                    "team",
                    "season",
                    "competition",
                    "opponent",
                    "home_away",
                    "venue",
                    "match_date",
                    "kickoff_time",
                    "round_label",
                    "match_length_minutes",
                    "half_length_minutes",
                    "status",
                )
            },
        ),
        (
            "Result details",
            {
                "fields": (
                    "team_score",
                    "opponent_score",
                    "result_resolution",
                    "penalties_team_score",
                    "penalties_opponent_score",
                    "player_of_the_match",
                )
            },
        ),
        (
            "Event and stats capture",
            {
                "fields": (
                    "event_capture_mode",
                )
            },
        ),
    )
