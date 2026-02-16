"""Models for core app."""

from uuid import uuid4

from django.db import models


class BaseModel(models.Model):
    """Abstract base model with common fields."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Player(BaseModel):
    """Player model for roommate assignment."""

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        """Return string representation of player."""
        return self.name


class SelectionLink(BaseModel):
    """Selection link for player roommate selection."""

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="selection_links",
    )
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of selection link."""
        return f"Link for {self.player.name} - {self.id}"


class RoommateSelection(BaseModel):
    """Roommate selection for a player."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("verified", "Verified"),
    ]

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="roommate_selections",
    )
    selection_link = models.ForeignKey(
        SelectionLink,
        on_delete=models.CASCADE,
        related_name="selections",
    )
    roommate_1 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="selected_by_as_1",
    )
    roommate_2 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="selected_by_as_2",
    )
    roommate_3 = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="selected_by_as_3",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
    )
    verification_code = models.CharField(max_length=2)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of roommate selection."""
        return f"{self.player.name}'s selection - {self.status}"


class Room(BaseModel):
    """Room assignment for players."""

    name = models.CharField(max_length=100)
    is_finalized = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        """Return string representation of room."""
        return self.name


class RoomAssignment(BaseModel):
    """Assignment of players to rooms."""

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="room_assignments",
    )

    class Meta:
        ordering = ["room", "player"]
        unique_together = ["room", "player"]

    def __str__(self) -> str:
        """Return string representation of room assignment."""
        return f"{self.player.name} in {self.room.name}"
