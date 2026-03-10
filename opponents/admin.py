"""
Admin configuration for the opponents app.

This file controls how opponent team records and opponent lineup entries
appear in Django admin.
"""

from django.contrib import admin

from .models import OpponentLineupEntry, OpponentTeam


@admin.register(OpponentTeam)
class OpponentTeamAdmin(admin.ModelAdmin):
    """Configure how the OpponentTeam model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "name",
        "short_name",
        "association",
        "suburb",
        "is_active",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "name",
        "short_name",
        "slug",
        "suburb",
        "association__name",
    )

    # Filters shown in the admin sidebar.
    list_filter = (
        "association",
        "is_active",
        "suburb",
    )

    # Automatically prefill the slug field from the opponent team name.
    prepopulated_fields = {"slug": ("name",)}


@admin.register(OpponentLineupEntry)
class OpponentLineupEntryAdmin(admin.ModelAdmin):
    """Configure how the OpponentLineupEntry model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "match",
        "opponent_team",
        "display_name",
        "shirt_number",
        "is_starter",
        "is_known",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "match__team__name",
        "match__opponent__name",
        "opponent_team__name",
        "display_name",
        "shirt_number",
    )

    # Filters shown in the admin sidebar.
    list_filter = (
        "match__season",
        "match__competition",
        "opponent_team",
        "is_starter",
        "is_known",
    )

    # Default ordering for the admin list page.
    ordering = (
        "-match__match_date",
        "opponent_team__name",
        "shirt_number",
        "display_name",
        "id",
    )

    # Make related match and opponent lookups easier to use.
    autocomplete_fields = ["match", "opponent_team"]

    # Group fields into a cleaner admin form layout.
    fieldsets = (
        (
            "Match context",
            {
                "fields": (
                    "match",
                    "opponent_team",
                )
            },
        ),
        (
            "Opponent participant details",
            {
                "fields": (
                    "display_name",
                    "shirt_number",
                    "is_starter",
                    "is_known",
                )
            },
        ),
    )

