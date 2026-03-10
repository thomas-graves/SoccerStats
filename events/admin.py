"""
Admin configuration for the events app.

This file controls how event-related models appear in Django admin.
It is designed to support structured manual post-match event entry by admins.

The admin workflow currently provides:
- a core MatchEvent form
- participant inlines
- qualifier inlines
- a separate MatchEventLink admin
"""

from django.contrib import admin
from django import forms

from .models import (
    MatchEvent,
    MatchEventLink,
    MatchEventParticipant,
    MatchEventQualifier,
    QUALIFIER_ALLOWED_TEXT_VALUES,
)


class MatchEventQualifierAdminForm(forms.ModelForm):
    """
    Admin form for event qualifiers.

    This form improves qualifier entry by:
    - using a dropdown for controlled text qualifiers
    - keeping the existing typed-value structure intact
    - reducing typing errors for common football vocabularies
    """

    class Meta:
        model = MatchEventQualifier
        fields = "__all__"

    class Media:
        """
        Load the custom admin JavaScript that makes qualifier text values
        reactively switch to dropdowns for controlled qualifier keys.
        """
        js = ("events/js/qualifier_admin.js",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Resolve the selected qualifier key for:
        # - existing objects
        # - bound admin forms
        # - inline forms with prefixes
        selected_key = self.data.get(self.add_prefix("key")) or getattr(self.instance, "key", None)

        # For controlled text qualifiers, swap the default text input for a dropdown.
        if selected_key in QUALIFIER_ALLOWED_TEXT_VALUES:
            choices = [("", "---------")] + [
                (value, value) for value in sorted(QUALIFIER_ALLOWED_TEXT_VALUES[selected_key])
            ]
            self.fields["text_value"].widget = forms.Select(choices=choices)


class MatchEventParticipantInline(admin.TabularInline):
    """
    Inline editor for event participants.

    Each participant row captures a role in the event, such as:
    - actor
    - recipient
    - goalkeeper
    - fouler
    - card receiver
    - substituted on / off
    """

    model = MatchEventParticipant

    # Explicitly tell Django which ForeignKey points back to MatchEvent.
    # This avoids ambiguity because other foreign keys in the model
    # may also point to event-related models.
    fk_name = "event"

    # Start with no blank rows, but allow admins to add more as needed.
    extra = 0

    # Make the related player lookup easier to use.
    autocomplete_fields = ["lineup_entry", "match_coach_assignment"]

    # Show a direct link to edit an existing inline object if needed.
    show_change_link = True

    # Keep the inline columns focused on match-entry needs.
    fields = (
        "role",
        "lineup_entry",
        "match_coach_assignment",
        "display_name",
        "shirt_number",
        "sequence_index",
    )


class MatchEventQualifierInline(admin.TabularInline):
    """
    Inline editor for event qualifiers.

    Qualifiers store event-specific metadata without bloating the core
    MatchEvent table. Examples include:
    - body_part
    - shot_on_target
    - chance_quality
    - set_piece_type
    - card_reason
    """

    model = MatchEventQualifier
    form = MatchEventQualifierAdminForm

    # Explicitly identify the parent event foreign key.
    fk_name = "event"

    # Start with no blank rows, but allow admins to add more as needed.
    extra = 0

    # These related lookups are helpful for typed qualifier values.
    autocomplete_fields = ["team_value", "player_value", "event_value"]

    # Show a direct link to edit an existing inline object if needed.
    show_change_link = True

    # Keep the inline focused on typed qualifier entry.
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


@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    """
    Configure how MatchEvent records are displayed and edited in Django admin.
    """

    # Inlines provide the main event-entry workflow.
    inlines = [MatchEventParticipantInline, MatchEventQualifierInline]

    # Helpful columns for browsing a match timeline in admin.
    list_display = (
        "match",
        "team_side",
        "event_type",
        "period",
        "minute",
        "added_minute",
        "second",
        "sequence_index",
        "outcome",
        "created_at",
        "updated_at",
    )

    # Support searching by match and free-text notes.
    search_fields = (
        "match__team__name",
        "match__opponent__name",
        "event_type",
        "notes",
    )

    # Useful filters for narrowing the event list.
    list_filter = (
        "event_type",
        "period",
        "outcome",
        "team_side",
        "match__season",
        "match__competition",
    )

    # Keep the timeline ordering intuitive.
    ordering = (
        "-match__match_date",
        "period",
        "minute",
        "added_minute",
        "second",
        "sequence_index",
        "id",
    )

    # Match remains a related lookup, but team is now represented by team_side.
    autocomplete_fields = ["match"]

    # Group the form into clearer sections for event entry.
    fieldsets = (
        (
            "Core event details",
            {
                "fields": (
                    "match",
                    "team_side",
                    "event_type",
                    "outcome",
                )
            },
        ),
        (
            "Timing",
            {
                "fields": (
                    "period",
                    "minute",
                    "added_minute",
                    "second",
                    "sequence_index",
                )
            },
        ),
        (
            "Optional pitch coordinates",
            {
                "fields": (
                    "start_x",
                    "start_y",
                    "end_x",
                    "end_y",
                )
            },
        ),
        (
            "Notes",
            {
                "fields": ("notes",)
            },
        ),
    )


@admin.register(MatchEventParticipant)
class MatchEventParticipantAdmin(admin.ModelAdmin):
    """
    Configure how MatchEventParticipant rows are displayed in Django admin.
    """

    list_display = (
        "event",
        "role",
        "lineup_entry",
        "match_coach_assignment",
        "display_name",
        "shirt_number",
        "sequence_index",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "event__match__team__name",
        "event__match__opponent__name",
        "role",
        "lineup_entry__registration__player__first_name",
        "lineup_entry__registration__player__last_name",
        "match_coach_assignment__coach_registration__coach__first_name",
        "match_coach_assignment__coach_registration__coach__last_name",
        "display_name",
    )

    list_filter = (
        "role",
        "event__match__season",
        "event__match__competition",
    )

    ordering = (
        "-event__match__match_date",
        "event__period",
        "event__minute",
        "event__added_minute",
        "event__second",
        "sequence_index",
        "id",
    )

    autocomplete_fields = ["event", "lineup_entry", "match_coach_assignment"]


@admin.register(MatchEventQualifier)
class MatchEventQualifierAdmin(admin.ModelAdmin):
    """
    Configure how MatchEventQualifier rows are displayed in Django admin.
    """

    form = MatchEventQualifierAdminForm

    list_display = (
        "event",
        "key",
        "value_type",
        "value",
        "sequence_index",
    )

    search_fields = (
        "event__match__team__name",
        "event__match__opponent__name",
        "key",
        "text_value",
    )

    list_filter = (
        "value_type",
        "key",
        "event__match__season",
        "event__match__competition",
    )

    ordering = (
        "-event__match__match_date",
        "event__period",
        "event__minute",
        "event__added_minute",
        "event__second",
        "sequence_index",
        "id",
    )

    autocomplete_fields = ["event", "team_value", "player_value", "event_value"]


@admin.register(MatchEventLink)
class MatchEventLinkAdmin(admin.ModelAdmin):
    """
    Configure how MatchEventLink rows are displayed in Django admin.
    """

    list_display = (
        "from_event",
        "link_type",
        "to_event",
        "sequence_index",
    )

    search_fields = (
        "from_event__match__team__name",
        "from_event__match__opponent__name",
        "to_event__match__team__name",
        "to_event__match__opponent__name",
        "link_type",
        "notes",
    )

    list_filter = (
        "link_type",
        "from_event__match__season",
        "from_event__match__competition",
    )

    ordering = (
        "-from_event__match__match_date",
        "sequence_index",
        "id",
    )

    autocomplete_fields = ["from_event", "to_event"]


