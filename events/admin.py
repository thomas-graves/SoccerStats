"""
Admin configuration for the events app.

This file controls how match event records appear in Django admin.
"""

from django.contrib import admin

from .models import (
    MatchEvent,
    MatchEventLink,
    MatchEventParticipant,
    MatchEventQualifier,
)


class MatchEventParticipantInline(admin.TabularInline):
    """
    Inline admin for event participants.

    This lets an admin attach one or more participants to an event,
    each with a role such as actor, assister, goalkeeper, fouled, etc.
    """
    model = MatchEventParticipant
    fk_name = "event"
    extra = 0

    # Show the most important participant fields directly in the event form.
    fields = (
        "role",
        "team",
        "player",
        "display_name",
        "shirt_number",
        "sequence_index",
    )

    # Keeps created/updated timestamps out of the inline form.
    show_change_link = True


class MatchEventQualifierInline(admin.TabularInline):
    """
    Inline admin for event qualifiers.

    Qualifiers store event-specific metadata using a typed key/value structure.
    Because qualifiers are flexible, we expose all typed value fields here.
    Admins should populate exactly one typed value field per row.
    """
    model = MatchEventQualifier
    fk_name = "event"
    extra = 0

    fields = (
        "key",
        "value_type",
        "text_value",
        "int_value",
        "decimal_value",
        "bool_value",
        "team_value",
        "player_value",
        "event_value",
        "sequence_index",
    )

    show_change_link = True


@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    """
    Main admin for match events.

    This is the core workflow screen for entering a match event,
    then attaching participants and qualifiers beneath it.
    """

    # Useful overview columns in the event list page.
    list_display = (
        "id",
        "match",
        "team",
        "event_type",
        "period",
        "minute",
        "added_minute",
        "second",
        "sequence_index",
        "outcome",
    )

    # Common filters for timeline/event browsing.
    list_filter = (
        "event_type",
        "period",
        "outcome",
        "team",
        "match",
    )

    # Lightweight search fields that do not assume any unknown Player/Team name fields.
    search_fields = (
        "notes",
        "id",
        "match__id",
    )

    # Helps keep timeline ordering consistent in the admin list page.
    ordering = (
        "match",
        "period",
        "minute",
        "added_minute",
        "second",
        "sequence_index",
        "id",
    )

    # Reduce clutter by grouping related fields.
    fieldsets = (
        (
            "Core event details",
            {
                "fields": (
                    "match",
                    "team",
                    "event_type",
                    "period",
                    "outcome",
                )
            },
        ),
        (
            "Timing",
            {
                "fields": (
                    "minute",
                    "added_minute",
                    "second",
                    "sequence_index",
                )
            },
        ),
        (
            "Pitch coordinates",
            {
                "fields": (
                    ("start_x", "start_y"),
                    ("end_x", "end_y"),
                ),
                "description": (
                    "Coordinates are stored as percentages from 0 to 100. "
                    "A visual pitch widget can be added later."
                ),
            },
        ),
        (
            "Notes",
            {
                "fields": ("notes",)
            },
        ),
    )

    # Add the two most important supporting models directly underneath the event.
    inlines = [
        MatchEventParticipantInline,
        MatchEventQualifierInline,
    ]


@admin.register(MatchEventParticipant)
class MatchEventParticipantAdmin(admin.ModelAdmin):
    """
    Standalone admin for participants.

    Useful for debugging, bulk inspection, and reverse lookups
    outside the parent MatchEvent form.
    """
    list_display = (
        "id",
        "event",
        "role",
        "team",
        "player",
        "display_name",
        "shirt_number",
        "sequence_index",
    )

    list_filter = (
        "role",
        "team",
    )

    search_fields = (
        "display_name",
        "id",
        "event__id",
    )

    ordering = (
        "event",
        "role",
        "sequence_index",
        "id",
    )


@admin.register(MatchEventQualifier)
class MatchEventQualifierAdmin(admin.ModelAdmin):
    """
    Standalone admin for qualifiers.

    This is especially useful while the flexible event schema is still
    being tested and refined.
    """
    list_display = (
        "id",
        "event",
        "key",
        "value_type",
        "sequence_index",
    )

    list_filter = (
        "value_type",
        "key",
    )

    search_fields = (
        "key",
        "id",
        "event__id",
        "text_value",
    )

    ordering = (
        "event",
        "key",
        "sequence_index",
        "id",
    )


@admin.register(MatchEventLink)
class MatchEventLinkAdmin(admin.ModelAdmin):
    """
    Standalone admin for event-to-event links.

    We keep this as a separate admin page for now because links are
    slightly more complex than participants/qualifiers and are easier
    to inspect in their own table first.
    """
    list_display = (
        "id",
        "from_event",
        "link_type",
        "to_event",
        "sequence_index",
    )

    list_filter = (
        "link_type",
    )

    search_fields = (
        "id",
        "from_event__id",
        "to_event__id",
        "notes",
    )

    ordering = (
        "from_event",
        "sequence_index",
        "id",
    )
