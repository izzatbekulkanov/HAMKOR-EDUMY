from django.urls import path
from .views import TableView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "student/",
        login_required(TableView.as_view(template_name="student.html")),
        name="main-student",
    ),
    path(
        "administration/",
        login_required(TableView.as_view(template_name="administrator.html")),
        name="main-administrator",
    ),
    path(
        "manager/",
        login_required(TableView.as_view(template_name="manager.html")),
        name="main-manager",
    ),
    path(
        "teacher/",
        login_required(TableView.as_view(template_name="teacher.html")),
        name="main-teacher",
    ),
    path(
        "director/",
        login_required(TableView.as_view(template_name="director.html")),
        name="main-director",
    ),
    path(
        "",
        login_required(TableView.as_view(template_name="main_page.html")),
        name="main-page-administrator",
    )
]
