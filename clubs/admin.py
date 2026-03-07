"""
Admin configuration for the clubs app.

This file controls how club-related models appear in Django admin.
"""

from django.contrib import admin

from .models import Club


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Configure how the Club model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = ("name", "short_name", "slug", "created_at", "updated_at")

    # Fields that can be searched in the admin search bar.
    search_fields = ("name", "short_name", "slug")

    # Automatically prefill the slug field from the club name.
    prepopulated_fields = {"slug": ("name",)}

    