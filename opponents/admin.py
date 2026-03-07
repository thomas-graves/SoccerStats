"""
Admin configuration for the opponents app.

This file controls how opponent team records appear in Django admin.
"""

from django.contrib import admin

from .models import OpponentTeam


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
