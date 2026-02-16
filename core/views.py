"""Views for core app."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView

from .models import Player, SelectionLink


class ProfileView(LoginRequiredMixin, TemplateView):
    """Admin profile view."""

    template_name = "core/profile.html"


class ProfilePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Password change view for admin profile."""

    template_name = "core/password_change.html"
    success_url = reverse_lazy("core:profile")

    def get_success_url(self) -> str:
        """Return success URL after password change."""
        return reverse_lazy("core:password_change_done")


class PasswordChangeDoneView(LoginRequiredMixin, TemplateView):
    """Password change success view."""

    template_name = "core/password_change_done.html"


class PlayerListView(LoginRequiredMixin, ListView):
    """List all players."""

    model = Player
    template_name = "core/player_list.html"
    context_object_name = "players"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        """Add selection links to context."""
        context = super().get_context_data(**kwargs)
        # Get the latest selection link for each player
        player_links = {}
        for player in context["players"]:
            latest_link = player.selection_links.first()
            if latest_link:
                player_links[player.id] = latest_link
        context["player_links"] = player_links
        return context


class PlayerCreateView(LoginRequiredMixin, CreateView):
    """Create a new player."""

    model = Player
    template_name = "core/player_form.html"
    fields = ["name", "phone", "email"]
    success_url = reverse_lazy("core:player_list")

    def form_valid(self, form):
        """Add success message on player creation."""
        messages.success(
            self.request, f"Player {form.instance.name} created successfully!"
        )
        return super().form_valid(form)


class GenerateSelectionLinkView(LoginRequiredMixin, View):
    """Generate a selection link for a player."""

    def post(self, request, player_id):
        """Create a new selection link for the player."""
        player = get_object_or_404(Player, id=player_id)
        selection_link = SelectionLink.objects.create(player=player)

        # Build the full URL for the selection page
        link_url = request.build_absolute_uri(
            reverse_lazy("core:roommate_select") + f"?id={selection_link.id}"
        )

        messages.success(
            request,
            f"Selection link generated for {player.name}!",
        )

        return redirect("core:player_list")
