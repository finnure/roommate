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
]
