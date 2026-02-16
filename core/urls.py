"""URL configuration for core app."""

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
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
    path(
        "players/<uuid:player_id>/generate-link/",
        views.GenerateSelectionLinkView.as_view(),
        name="generate_link",
    ),
    path("select/", views.RoommateSelectView.as_view(), name="roommate_select"),
    path("verify/", views.VerifySelectionView.as_view(), name="verify_selection"),
]
