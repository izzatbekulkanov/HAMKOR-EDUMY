from django.urls import path
from .views import TableView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "directors/",
        login_required(TableView.as_view(template_name="directors.html")),
        name="user-directors",
    ),
    path(
        "teachers/",
        login_required(TableView.as_view(template_name="teachers.html")),
        name="user-teachers",
    ),
    path(
        "students/",
        login_required(TableView.as_view(template_name="students.html")),
        name="user-students",
    ),
    path(
        "administrators/",
        login_required(TableView.as_view(template_name="admins.html")),
        name="user-administrator",
    )
]
