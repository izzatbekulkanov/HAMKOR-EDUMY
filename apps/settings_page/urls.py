from django.urls import path

from config.decorators import verified_required
from .views import SettingsView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path(
        "logs/",
        verified_required(SettingsView.as_view(template_name="log.html")),
        name="setting-log",
    ),
    path(
        "cashback/",
        verified_required(SettingsView.as_view(template_name="cashback.html")),
        name="setting-cashback",
    ),
    path(
        "regions/",
        verified_required(SettingsView.as_view(template_name="regions.html")),
        name="setting-regions",
    ),
    path(
        "role",
        verified_required(SettingsView.as_view(template_name="role.html")),
        name="setting-role",
    )
]
