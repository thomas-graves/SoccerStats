"""
Admin configuration for the lineups app.

This file controls how lineup-related models appear in Django admin.
"""

from django.contrib import admin

from .models import LineupEntry


@admin.register(LineupEntry)
class LineupEntryAdmin(admin.ModelAdmin):
    """Configure how the LineupEntry model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "match",
        "registration",
        "role",
        "position_label",
        "shirt_number",
        "is_captain",
        "sort_order",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "match__opponent_name",
        "registration__player__first_name",
        "registration__player__last_name",
        "registration__team__name",
        "position_label",
    )

    # Filters shown in the admin sidebar.
    list_filter = (
        "role",
        "is_captain",
        "registration__season",
        "registration__team",
    )

    # Default ordering for the admin list page.
    ordering = (
        "-match__match_date",
        "role",
        "sort_order",
        "registration__player__last_name",
    )
