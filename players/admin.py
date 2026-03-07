"""
Admin configuration for the players app.

This file controls how player-related models appear in Django admin.
"""

from django.contrib import admin

from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Configure how the Player model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "first_name",
        "last_name",
        "preferred_name",
        "club",
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
    )

    # Filters shown in the admin sidebar.
    list_filter = ("club", "is_active")

    # Automatically prefill the slug field from the player's first and last name.
    prepopulated_fields = {"slug": ("first_name", "last_name")}
