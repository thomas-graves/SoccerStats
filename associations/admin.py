"""
Admin configuration for the associations app.

This file controls how association-related models appear in Django admin.
"""

from django.contrib import admin

from .models import Association


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    """Configure how the Association model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "name",
        "short_name",
        "website_url",
        "is_active",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "name",
        "short_name",
        "slug",
        "website_url",
    )

    # Filters shown in the admin sidebar.
    list_filter = ("is_active",)

    # Automatically prefill the slug field from the association name.
    prepopulated_fields = {"slug": ("name",)}
