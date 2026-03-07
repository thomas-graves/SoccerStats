"""
Admin configuration for the teams app.

This file controls how team-related models appear in Django admin.
"""

from django.contrib import admin

from .models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Configure how the Team model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = ("name", "short_name", "club", "slug", "created_at", "updated_at")

    # Fields that can be searched in the admin search bar.
    search_fields = ("name", "short_name", "slug", "club__name")

    # Filters shown in the admin sidebar.
    list_filter = ("club",)

    # Automatically prefill the slug field from the team name.
    prepopulated_fields = {"slug": ("name",)}

