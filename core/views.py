"""Views for core app."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import TemplateView


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
