from django.urls import path

from config.decorators import verified_required
from .views import TableView, clear_toastr_session

urlpatterns = [
    path(
        "student/",
        verified_required(TableView.as_view(template_name="student.html")),
        name="main-student",
    ),
    path(
        "administration/",
        verified_required(TableView.as_view(template_name="administrator.html")),
        name="main-administrator",
    ),
    path(
        "manager/",
        verified_required(TableView.as_view(template_name="manager.html")),
        name="main-manager",
    ),
    path(
        "teacher/",
        verified_required(TableView.as_view(template_name="teacher.html")),
        name="main-teacher",
    ),
    path(
        "director/",
        verified_required(TableView.as_view(template_name="director.html")),
        name="main-director",
    ),
    path(
        "",
        verified_required(TableView.as_view(template_name="main_page.html")),
        name="main-page-administrator",
    ),
    path(
        "waiting/",
        TableView.as_view(template_name="waiting.html"),
        name="waiting",
    ),
    path('clear-toastr-session/', clear_toastr_session, name='clear_toastr_session')
]
