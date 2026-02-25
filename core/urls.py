"""URL configuration for core app."""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/password/",
        views.ProfilePasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "profile/password/done/",
        views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("players/", views.PlayerListView.as_view(), name="player_list"),
    path("players/create/", views.PlayerCreateView.as_view(), name="player_create"),
    path("players/import/", views.PlayerImportView.as_view(), name="player_import"),
    path(
        "players/<uuid:player_id>/generate-link/",
        views.GenerateSelectionLinkView.as_view(),
        name="generate_link",
    ),
    path("selections/", views.SelectionsView.as_view(), name="selections"),
    path(
        "selections/export/",
        views.ExportSelectionsView.as_view(),
        name="export_selections",
    ),
    path("select/", views.RoommateSelectView.as_view(), name="roommate_select"),
    path("verify/", views.VerifySelectionView.as_view(), name="verify_selection"),
    path(
        "assignments/generate/",
        views.GenerateRoomAssignmentsView.as_view(),
        name="generate_assignments",
    ),
    path(
        "assignments/update/",
        views.UpdateRoomAssignmentView.as_view(),
        name="update_assignment",
    ),
    path(
        "assignments/validate/",
        views.ValidateAssignmentsView.as_view(),
        name="validate_assignments",
    ),
    path(
        "rooms/<uuid:room_id>/delete/",
        views.DeleteRoomView.as_view(),
        name="delete_room",
    ),
    path("rooms/arrange/", views.RoomArrangeView.as_view(), name="room_arrange"),
    path(
        "rooms/arrange/save/",
        views.SaveRoomArrangeView.as_view(),
        name="save_room_arrange",
    ),
    path("health/", views.health_check, name="health_check"),
]
