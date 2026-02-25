"""Views for core app."""

import csv
import json
import math
from collections import defaultdict
from typing import Dict, List, Set

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView

from .models import Player, Room, RoomAssignment, RoommateSelection, SelectionLink


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


class PlayerImportView(LoginRequiredMixin, TemplateView):
    """Import players from comma-separated text."""

    template_name = "core/player_import.html"

    def post(self, request):
        """Process the import data."""
        import_data = request.POST.get("import_data", "").strip()

        if not import_data:
            messages.error(request, "Please provide data to import.")
            return redirect("core:player_import")

        lines = import_data.split("\n")
        inserted = []
        errors = []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            parts = [p.strip() for p in line.split(",")]

            # Validate line has 1-3 values
            if len(parts) < 1 or len(parts) > 3:
                errors.append(
                    {
                        "line": line_num,
                        "data": line,
                        "error": f"Invalid format: expected 1-3 comma-separated values, got {len(parts)}",
                    }
                )
                continue

            name = parts[0]
            phone = parts[1] if len(parts) > 1 else None
            email = None

            # If there are 3 parts, third should be email
            if len(parts) == 3:
                # Validate email format (basic check)
                if "@" in parts[2] and "." in parts[2]:
                    email = parts[2]
                else:
                    errors.append(
                        {
                            "line": line_num,
                            "data": line,
                            "error": f"Invalid email format: {parts[2]}",
                        }
                    )
                    continue
            # If there are 2 parts, check if second is email
            elif len(parts) == 2:
                if "@" in parts[1] and "." in parts[1]:
                    email = parts[1]
                    phone = None

            # Validate name is not empty
            if not name:
                errors.append(
                    {"line": line_num, "data": line, "error": "Name cannot be empty"}
                )
                continue

            # Create the player
            try:
                with transaction.atomic():
                    player = Player.objects.create(name=name, phone=phone, email=email)
                    inserted.append(
                        {"name": name, "phone": phone or "-", "email": email or "-"}
                    )
            except Exception as e:
                errors.append({"line": line_num, "data": line, "error": str(e)})

        # Build success/error messages
        if inserted:
            messages.success(
                request, f"Successfully imported {len(inserted)} player(s)."
            )

        if errors:
            messages.warning(
                request, f"Failed to import {len(errors)} line(s). See details below."
            )

        return render(
            request,
            self.template_name,
            {"inserted": inserted, "errors": errors, "import_data": import_data},
        )


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
            messages.error(request, "Vinsamlegast veldu alla 3 herbergisfélaga.")
            return redirect(f"{reverse_lazy('core:roommate_select')}?id={link_id}")

        # Validate no duplicates
        if len(set([roommate_1_id, roommate_2_id, roommate_3_id])) != 3:
            messages.error(request, "Þú getur ekki valið sama leikmanninn tvisvar.")
            return redirect(f"{reverse_lazy('core:roommate_select')}?id={link_id}")

        # Get roommate objects
        roommate_1 = get_object_or_404(Player, id=roommate_1_id)
        roommate_2 = get_object_or_404(Player, id=roommate_2_id)
        roommate_3 = get_object_or_404(Player, id=roommate_3_id)

        # Validate none of the roommates is the current player
        if player.id in [roommate_1.id, roommate_2.id, roommate_3.id]:
            messages.error(
                request, "Þú getur ekki valið sjálfan þig sem herbergisfélaga."
            )
            return redirect(f"{reverse_lazy('core:roommate_select')}?id={link_id}")

        # Create or update the selection directly as verified
        selection, created = RoommateSelection.objects.update_or_create(
            selection_link=selection_link,
            defaults={
                "player": player,
                "roommate_1": roommate_1,
                "roommate_2": roommate_2,
                "roommate_3": roommate_3,
                "status": "verified",
                "verification_code": "",  # No longer needed
            },
        )

        # Mark the selection link as used
        selection_link.is_used = True
        selection_link.save()

        return render(
            request,
            "core/selection_verified.html",
            {
                "selection": selection,
            },
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


class DashboardView(LoginRequiredMixin, TemplateView):
    """Admin dashboard with statistics and room assignments."""

    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        """Get dashboard statistics and room assignments."""
        context = super().get_context_data(**kwargs)

        # Statistics
        total_players = Player.objects.count()
        total_links = SelectionLink.objects.count()
        unused_links = SelectionLink.objects.filter(is_used=False).count()
        used_links = SelectionLink.objects.filter(is_used=True).count()

        # Players with links
        players_with_links = (
            Player.objects.filter(selection_links__isnull=False).distinct().count()
        )
        players_without_links = total_players - players_with_links

        # Selections
        draft_selections = RoommateSelection.objects.filter(status="draft").count()
        verified_selections = RoommateSelection.objects.filter(
            status="verified"
        ).count()

        # Check if we can generate room assignments
        can_generate = (
            total_players > 0
            and players_without_links == 0
            and verified_selections == total_players
        )

        context.update(
            {
                "total_players": total_players,
                "total_links": total_links,
                "unused_links": unused_links,
                "used_links": used_links,
                "players_with_links": players_with_links,
                "players_without_links": players_without_links,
                "draft_selections": draft_selections,
                "verified_selections": verified_selections,
                "can_generate": can_generate,
            }
        )

        # Get current room assignments
        rooms = Room.objects.prefetch_related("assignments__player").all()
        context["rooms"] = rooms

        # Get all players for assignment dropdown
        context["all_players"] = Player.objects.all().order_by("name")

        return context


class GenerateRoomAssignmentsView(LoginRequiredMixin, View):
    """Generate suggested room assignments based on selections."""

    def post(self, request):
        """Generate room assignments using a matching algorithm."""
        # Get all verified selections
        selections = RoommateSelection.objects.filter(status="verified").select_related(
            "player", "roommate_1", "roommate_2", "roommate_3"
        )

        if not selections.exists():
            messages.error(request, "No verified selections found.")
            return redirect("core:dashboard")

        # Build preference graph
        preferences = defaultdict(list)
        for selection in selections:
            preferences[selection.player.id] = [
                selection.roommate_1.id,
                selection.roommate_2.id,
                selection.roommate_3.id,
            ]

        # Generate room assignments
        rooms_data = self._generate_assignments(preferences, selections)

        # Clear existing non-finalized rooms
        Room.objects.filter(is_finalized=False).delete()

        # Create new room assignments
        with transaction.atomic():
            for idx, player_ids in enumerate(rooms_data, 1):
                room = Room.objects.create(name=f"Room {idx}")
                for player_id in player_ids:
                    player = Player.objects.get(id=player_id)
                    RoomAssignment.objects.create(room=room, player=player)

        messages.success(
            request,
            f"Generated {len(rooms_data)} room assignments! Review and adjust as needed.",
        )
        return redirect("core:dashboard")

    def _generate_assignments(
        self, preferences: Dict[str, List[str]], selections
    ) -> List[List[str]]:
        """Generate room assignments based on mutual preferences."""
        all_players = set(preferences.keys())
        assigned = set()
        rooms = []

        # First pass: Find groups with mutual preferences (3-person rooms)
        for player_id in list(all_players):
            if player_id in assigned:
                continue

            player_prefs = preferences[player_id]

            # Check if this player and their top 2 choices mutually prefer each other
            for i in range(len(player_prefs) - 1):
                for j in range(i + 1, len(player_prefs)):
                    roommate1_id = player_prefs[i]
                    roommate2_id = player_prefs[j]

                    if roommate1_id in assigned or roommate2_id in assigned:
                        continue

                    # Check mutual preferences
                    if (
                        roommate1_id in preferences
                        and roommate2_id in preferences
                        and player_id in preferences[roommate1_id]
                        and player_id in preferences[roommate2_id]
                        and roommate2_id in preferences[roommate1_id]
                        and roommate1_id in preferences[roommate2_id]
                    ):
                        # Found a mutual match!
                        rooms.append([player_id, roommate1_id, roommate2_id])
                        assigned.update([player_id, roommate1_id, roommate2_id])
                        break
                if player_id in assigned:
                    break

        # Second pass: Assign remaining players based on preferences
        unassigned = list(all_players - assigned)
        while unassigned:
            if len(unassigned) >= 3:
                # Take first unassigned player and their top 2 available preferences
                player_id = unassigned[0]
                player_prefs = preferences[player_id]

                room_members = [player_id]
                for pref_id in player_prefs:
                    if pref_id in unassigned and len(room_members) < 3:
                        room_members.append(pref_id)

                # Fill remaining spots if needed
                while len(room_members) < 3 and unassigned:
                    for uid in unassigned:
                        if uid not in room_members:
                            room_members.append(uid)
                            break

                if len(room_members) == 3:
                    rooms.append(room_members)
                    for member_id in room_members:
                        if member_id in unassigned:
                            unassigned.remove(member_id)
                else:
                    break
            else:
                # Fewer than 3 left - add to existing room or create partial
                rooms.append(unassigned[:3])
                unassigned = unassigned[3:]

        return rooms


class UpdateRoomAssignmentView(LoginRequiredMixin, View):
    """Update room assignments."""

    def post(self, request):
        """Update a room's player assignments."""
        room_id = request.POST.get("room_id")
        player_ids = request.POST.getlist("player_ids")

        if not room_id:
            return JsonResponse({"error": "Room ID required"}, status=400)

        room = get_object_or_404(Room, id=room_id)

        if room.is_finalized:
            return JsonResponse({"error": "Cannot modify finalized room"}, status=400)

        # Update assignments
        with transaction.atomic():
            # Remove existing assignments
            room.assignments.all().delete()

            # Add new assignments
            for player_id in player_ids:
                if player_id:
                    player = Player.objects.get(id=player_id)
                    RoomAssignment.objects.create(room=room, player=player)

        messages.success(request, f"Updated {room.name}")
        return redirect("core:dashboard")


class ValidateAssignmentsView(LoginRequiredMixin, View):
    """Validate that all players are assigned to rooms."""

    def post(self, request):
        """Validate room assignments."""
        total_players = Player.objects.count()
        assigned_players = RoomAssignment.objects.values("player").distinct().count()

        if total_players == 0:
            messages.warning(request, "No players in the system.")
            return redirect("core:dashboard")

        if assigned_players == total_players:
            messages.success(
                request, f"✓ All {total_players} players are assigned to rooms!"
            )
        else:
            unassigned = total_players - assigned_players
            messages.error(
                request,
                f"✗ {unassigned} player(s) not assigned. Total: {assigned_players}/{total_players}",
            )

            # Find which players are unassigned
            assigned_player_ids = RoomAssignment.objects.values_list(
                "player_id", flat=True
            )
            unassigned_players = Player.objects.exclude(
                id__in=assigned_player_ids
            ).values_list("name", flat=True)

            if unassigned_players:
                messages.info(
                    request, f"Unassigned players: {', '.join(unassigned_players)}"
                )

        return redirect("core:dashboard")


class DeleteRoomView(LoginRequiredMixin, View):
    """Delete a room and its assignments."""

    def post(self, request, room_id):
        """Delete a room."""
        room = get_object_or_404(Room, id=room_id)

        if room.is_finalized:
            messages.error(request, "Cannot delete finalized room.")
            return redirect("core:dashboard")

        room_name = room.name
        room.delete()
        messages.success(request, f"Deleted {room_name}")
        return redirect("core:dashboard")


class SelectionsView(LoginRequiredMixin, ListView):
    """View all roommate selections."""

    model = RoommateSelection
    template_name = "core/selections.html"
    context_object_name = "selections"
    paginate_by = 50

    def get_queryset(self):
        """Get all selections with related data."""
        return RoommateSelection.objects.select_related(
            "player", "roommate_1", "roommate_2", "roommate_3", "selection_link"
        ).order_by("-created_at")

    def get_context_data(self, **kwargs):
        """Add statistics to context."""
        context = super().get_context_data(**kwargs)

        # Statistics
        total_selections = RoommateSelection.objects.count()
        verified_selections = RoommateSelection.objects.filter(
            status="verified"
        ).count()
        draft_selections = RoommateSelection.objects.filter(status="draft").count()

        context.update(
            {
                "total_selections": total_selections,
                "verified_selections": verified_selections,
                "draft_selections": draft_selections,
            }
        )

        return context


class ExportSelectionsView(LoginRequiredMixin, View):
    """Export all verified selections to CSV."""

    def get(self, request):
        """Generate and return CSV file."""
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="roommate_selections.csv"'
        )

        # Create CSV writer
        writer = csv.writer(response)

        # Write header row
        writer.writerow(
            [
                "Player Name",
                "Player Email",
                "Player Phone",
                "First Choice",
                "Second Choice",
                "Third Choice",
                "Status",
                "Submitted At",
            ]
        )

        # Get all verified selections
        selections = (
            RoommateSelection.objects.select_related(
                "player", "roommate_1", "roommate_2", "roommate_3"
            )
            .filter(status="verified")
            .order_by("player__name")
        )

        # Write data rows
        for selection in selections:
            writer.writerow(
                [
                    selection.player.name,
                    selection.player.email,
                    selection.player.phone,
                    selection.roommate_1.name,
                    selection.roommate_2.name,
                    selection.roommate_3.name,
                    selection.status.capitalize(),
                    selection.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        return response


class RoomArrangeView(LoginRequiredMixin, View):
    """Drag-and-drop room arrangement page."""

    template_name = "core/room_arrange.html"

    def get(self, request):
        """Render the arrangement page with players and rooms serialised for JS."""
        # All players who have submitted at least one selection (any status)
        selections = (
            RoommateSelection.objects.select_related(
                "player", "roommate_1", "roommate_2", "roommate_3"
            )
            .order_by("player__name", "-created_at")
            .distinct()
        )

        # Deduplicate: keep only the latest selection per player
        seen: Set[str] = set()
        player_selections: Dict[str, dict] = {}
        for sel in selections:
            pid = str(sel.player.id)
            if pid not in seen:
                seen.add(pid)
                player_selections[pid] = {
                    "id": pid,
                    "name": sel.player.name,
                    "choices": [
                        sel.roommate_1.name,
                        sel.roommate_2.name,
                        sel.roommate_3.name,
                    ],
                }

        # Current room assignments
        rooms_qs = Room.objects.prefetch_related("assignments__player").order_by(
            "name"
        )
        rooms_data = []
        assigned_player_ids: Set[str] = set()
        for room in rooms_qs:
            members = []
            for assignment in room.assignments.all():
                pid = str(assignment.player.id)
                members.append(pid)
                assigned_player_ids.add(pid)
            rooms_data.append(
                {
                    "id": str(room.id),
                    "name": room.name,
                    "is_finalized": room.is_finalized,
                    "player_ids": members,
                }
            )

        # Players not yet in any room
        unassigned = [
            p for pid, p in player_selections.items() if pid not in assigned_player_ids
        ]

        n_players = len(player_selections)
        needed_rooms = math.ceil(n_players / 3) + 1 if n_players > 0 else 1

        context = {
            "players_json": json.dumps(player_selections),
            "rooms_json": json.dumps(rooms_data),
            "unassigned_json": json.dumps([p["id"] for p in unassigned]),
            "needed_rooms": needed_rooms,
            "n_players": n_players,
        }
        return render(request, self.template_name, context)


class SaveRoomArrangeView(LoginRequiredMixin, View):
    """AJAX endpoint — save the dragged room layout to the database."""

    def post(self, request):
        """Accept JSON body and persist room assignments atomically."""
        try:
            payload = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        rooms_payload = payload.get("rooms", [])
        if not isinstance(rooms_payload, list):
            return JsonResponse({"error": "Invalid payload shape"}, status=400)

        try:
            with transaction.atomic():
                # Track which DB rooms we touched so we can rename sequentially
                room_counter = 0
                for item in rooms_payload:
                    room_id = item.get("room_id")  # None / "new" / UUID string
                    player_ids = item.get("player_ids", [])
                    room_name = item.get("name", "")

                    if not player_ids:
                        # Empty room — if it exists in DB and is not finalized, delete it
                        if room_id and room_id not in ("new", None):
                            try:
                                room = Room.objects.get(id=room_id)
                                if not room.is_finalized:
                                    room.delete()
                            except Room.DoesNotExist:
                                pass
                        continue

                    room_counter += 1

                    if room_id and room_id not in ("new",):
                        # Existing room
                        try:
                            room = Room.objects.get(id=room_id)
                        except Room.DoesNotExist:
                            room = Room.objects.create(name=room_name or f"Room {room_counter}")
                    else:
                        room = Room.objects.create(name=room_name or f"Room {room_counter}")

                    if room.is_finalized:
                        # Never touch finalized rooms
                        continue

                    # Rebuild assignments
                    room.assignments.all().delete()
                    for pid in player_ids:
                        try:
                            player = Player.objects.get(id=pid)
                            RoomAssignment.objects.create(room=room, player=player)
                        except Player.DoesNotExist:
                            pass

        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=500)

        return JsonResponse({"success": True})


def health_check(request):
    """Simple health check endpoint for Docker/k8s."""
    return JsonResponse({"status": "healthy", "service": "roommate"})
