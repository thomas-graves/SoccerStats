"""
Admin configuration for the seasons app.

This file controls how season-related models appear in Django admin.
"""

from django.contrib import admin

from .models import Season


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    """Configure how the Season model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "name",
        "club",
        "start_date",
        "end_date",
        "is_current",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = ("name", "slug", "club__name")

    # Filters shown in the admin sidebar.
    list_filter = ("club", "is_current")

    # Automatically prefill the slug field from the season name.
    prepopulated_fields = {"slug": ("name",)}
