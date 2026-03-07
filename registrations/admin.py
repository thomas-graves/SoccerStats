"""
Admin configuration for the registrations app.

This file controls how player registration records appear in Django admin.
"""

from django.contrib import admin

from .models import PlayerRegistration


@admin.register(PlayerRegistration)
class PlayerRegistrationAdmin(admin.ModelAdmin):
    """Configure how the PlayerRegistration model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "player",
        "team",
        "season",
        "squad_number",
        "is_active",
        "joined_on",
        "left_on",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "player__first_name",
        "player__last_name",
        "player__preferred_name",
        "team__name",
        "season__name",
    )

    # Filters shown in the admin sidebar.
    list_filter = ("season", "team", "is_active")

    # Default ordering for the admin list page.
    ordering = ("season__name", "team__name", "player__last_name", "player__first_name")
