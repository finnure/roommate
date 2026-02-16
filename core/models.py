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
