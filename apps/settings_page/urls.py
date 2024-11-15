from django.urls import path
from .views import TableView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "logs/",
        login_required(TableView.as_view(template_name="log.html")),
        name="setting-log",
    ),
    path(
        "role",
        login_required(TableView.as_view(template_name="role.html")),
        name="setting-role",
    )
]
