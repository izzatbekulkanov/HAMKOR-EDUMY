from django.urls import path
from .views import SettingsView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path(
        "logs/",
        login_required(SettingsView.as_view(template_name="log.html")),
        name="setting-log",
    ),
    path(
        "cashback/",
        login_required(SettingsView.as_view(template_name="cashback.html")),
        name="setting-cashback",
    ),
    path(
        "regions/",
        login_required(SettingsView.as_view(template_name="regions.html")),
        name="setting-regions",
    ),
    path(
        "role",
        login_required(SettingsView.as_view(template_name="role.html")),
        name="setting-role",
    )
]
