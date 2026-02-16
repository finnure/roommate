"""Admin configuration for core app."""

from django.contrib import admin

from .models import Player, SelectionLink


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
