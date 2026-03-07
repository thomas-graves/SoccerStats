"""
Admin configuration for the venues app.

This file controls how venue-related models appear in Django admin.
"""

from django.contrib import admin

from .models import Venue


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    """Configure how the Venue model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "name",
        "short_name",
        "club",
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
        "address",
        "suburb",
        "club__name",
    )

    # Filters shown in the admin sidebar.
    list_filter = ("club", "is_active", "suburb")

    # Automatically prefill the slug field from the venue name.
    prepopulated_fields = {"slug": ("name",)}
