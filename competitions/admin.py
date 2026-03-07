"""
Admin configuration for the competitions app.

This file controls how competition-related models appear in Django admin.
"""

from django.contrib import admin

from .models import Competition


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    """Configure how the Competition model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = ("name", "short_name", "club", "slug", "created_at", "updated_at")

    # Fields that can be searched in the admin search bar.
    search_fields = ("name", "short_name", "slug", "club__name")

    # Filters shown in the admin sidebar.
    list_filter = ("club",)

    # Automatically prefill the slug field from the competition name.
    prepopulated_fields = {"slug": ("name",)}

