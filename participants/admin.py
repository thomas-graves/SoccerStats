"""
Admin configuration for the participants app.

This file controls how competition participant records appear in Django admin.
"""

from django.contrib import admin

from .models import CompetitionParticipant


@admin.register(CompetitionParticipant)
class CompetitionParticipantAdmin(admin.ModelAdmin):
    """Configure how the CompetitionParticipant model is displayed in Django admin."""

    # Columns shown in the admin list view.
    list_display = (
        "name",
        "season",
        "competition",
        "team",
        "opponent_team",
        "is_active",
        "created_at",
        "updated_at",
    )

    # Fields that can be searched in the admin search bar.
    search_fields = (
        "display_name",
        "team__name",
        "team__short_name",
        "opponent_team__name",
        "opponent_team__short_name",
        "competition__name",
        "season__name",
    )

    # Filters shown in the admin sidebar.
    list_filter = (
        "season",
        "competition",
        "is_active",
    )

    # Default ordering for the admin list page.
    ordering = (
        "season__name",
        "competition__name",
        "display_name",
        "id",
    )

    # Group fields into clearer sections in the admin form.
    fieldsets = (
        (
            "Participant details",
            {
                "fields": (
                    "season",
                    "competition",
                    "team",
                    "opponent_team",
                    "display_name",
                    "is_active",
                )
            },
        ),
    )
