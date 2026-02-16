"""Admin configuration for core app."""

from django.contrib import admin

from .models import Player, Room, RoomAssignment, RoommateSelection, SelectionLink


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Admin for Player model."""

    list_display = ["name", "phone", "email", "created_at"]
    search_fields = ["name", "email", "phone"]
    list_filter = ["created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(SelectionLink)
class SelectionLinkAdmin(admin.ModelAdmin):
    """Admin for SelectionLink model."""

    list_display = ["player", "id", "is_used", "created_at"]
    list_filter = ["is_used", "created_at"]
    search_fields = ["player__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["player"]


@admin.register(RoommateSelection)
class RoommateSelectionAdmin(admin.ModelAdmin):
    """Admin for RoommateSelection model."""

    list_display = [
        "player",
        "roommate_1",
        "roommate_2",
        "roommate_3",
        "status",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = [
        "player__name",
        "roommate_1__name",
        "roommate_2__name",
        "roommate_3__name",
    ]
    readonly_fields = ["id", "verification_code", "created_at", "updated_at"]
    raw_id_fields = [
        "player",
        "selection_link",
        "roommate_1",
        "roommate_2",
        "roommate_3",
    ]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin for Room model."""

    list_display = ["name", "is_finalized", "created_at"]
    list_filter = ["is_finalized", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(RoomAssignment)
class RoomAssignmentAdmin(admin.ModelAdmin):
    """Admin for RoomAssignment model."""

    list_display = ["room", "player", "created_at"]
    list_filter = ["room", "created_at"]
    search_fields = ["room__name", "player__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["room", "player"]
