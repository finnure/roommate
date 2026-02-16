"""Views for core app."""

import random

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView

from .models import Player, RoommateSelection, SelectionLink


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


class RoommateSelectView(View):
    """Roommate selection view."""

    def get(self, request):
        """Display the roommate selection form."""
        link_id = request.GET.get("id")
        if not link_id:
            raise Http404("Selection link not found")

        selection_link = get_object_or_404(SelectionLink, id=link_id)
        player = selection_link.player

        # Get all other players (exclude the current player)
        other_players = Player.objects.exclude(id=player.id).order_by("name")

        # Check if there's already a verified selection for this link
        existing_selection = RoommateSelection.objects.filter(
            selection_link=selection_link, status="verified"
        ).first()

        if existing_selection:
            return render(
                request,
                "core/selection_complete.html",
                {
                    "player": player,
                    "selection": existing_selection,
                },
            )

        context = {
            "player": player,
            "other_players": other_players,
            "link_id": link_id,
        }
        return render(request, "core/roommate_select.html", context)

    def post(self, request):
        """Process the roommate selection form."""
        link_id = request.POST.get("link_id")
        if not link_id:
            raise Http404("Selection link not found")

        selection_link = get_object_or_404(SelectionLink, id=link_id)
        player = selection_link.player

        # Get the selected roommates
        roommate_1_id = request.POST.get("roommate_1")
        roommate_2_id = request.POST.get("roommate_2")
        roommate_3_id = request.POST.get("roommate_3")

        # Validate all selections are made
        if not all([roommate_1_id, roommate_2_id, roommate_3_id]):
            messages.error(request, "Please select all 3 roommates.")
            return redirect(f"{reverse_lazy('core:roommate_select')}?id={link_id}")

        # Validate no duplicates
        if len(set([roommate_1_id, roommate_2_id, roommate_3_id])) != 3:
            messages.error(request, "You cannot select the same roommate twice.")
            return redirect(f"{reverse_lazy('core:roommate_select')}?id={link_id}")

        # Get roommate objects
        roommate_1 = get_object_or_404(Player, id=roommate_1_id)
        roommate_2 = get_object_or_404(Player, id=roommate_2_id)
        roommate_3 = get_object_or_404(Player, id=roommate_3_id)

        # Validate none of the roommates is the current player
        if player.id in [roommate_1.id, roommate_2.id, roommate_3.id]:
            messages.error(request, "You cannot select yourself as a roommate.")
            return redirect(f"{reverse_lazy('core:roommate_select')}?id={link_id}")

        # Generate 2-digit verification code
        verification_code = str(random.randint(10, 99))

        # Create or update the draft selection
        selection, created = RoommateSelection.objects.update_or_create(
            selection_link=selection_link,
            status="draft",
            defaults={
                "player": player,
                "roommate_1": roommate_1,
                "roommate_2": roommate_2,
                "roommate_3": roommate_3,
                "verification_code": verification_code,
            },
        )

        # TODO: Send verification code via SMS/email
        # For now, we'll just display it on the verification page

        return redirect(
            f"{reverse_lazy('core:verify_selection')}?selection_id={selection.id}"
        )


class VerifySelectionView(View):
    """Verify selection with code."""

    def get(self, request):
        """Display verification page."""
        selection_id = request.GET.get("selection_id")
        if not selection_id:
            raise Http404("Selection not found")

        selection = get_object_or_404(
            RoommateSelection, id=selection_id, status="draft"
        )

        context = {
            "selection": selection,
            "verification_code": selection.verification_code,  # For demo purposes
        }
        return render(request, "core/verify_selection.html", context)

    def post(self, request):
        """Process verification code."""
        selection_id = request.POST.get("selection_id")
        entered_code = request.POST.get("verification_code")

        if not selection_id or not entered_code:
            messages.error(request, "Invalid request.")
            return redirect("core:player_list")

        selection = get_object_or_404(
            RoommateSelection, id=selection_id, status="draft"
        )

        if entered_code != selection.verification_code:
            messages.error(request, "Invalid verification code. Please try again.")
            return redirect(
                f"{reverse_lazy('core:verify_selection')}?selection_id={selection.id}"
            )

        # Mark selection as verified
        selection.status = "verified"
        selection.save()

        # Mark the selection link as used
        selection.selection_link.is_used = True
        selection.selection_link.save()

        return render(
            request,
            "core/selection_verified.html",
            {
                "selection": selection,
            },
        )
