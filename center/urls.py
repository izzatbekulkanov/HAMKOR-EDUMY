from django.urls import path
from .views import TableView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "course/",
        login_required(TableView.as_view(template_name="course.html")),
        name="course",
    ),
    path(
        "learning-center/",
        login_required(TableView.as_view(template_name="learning_center.html")),
        name="learning-center",
    ),
    path(
        "learning-groups/",
        login_required(TableView.as_view(template_name="learning_groups.html")),
        name="learning-groups",
    ),
    path(
        "learning-statistics/",
        login_required(TableView.as_view(template_name="learning_statistics.html")),
        name="learning-statistics",
    ),
    path(
        "occupations/",
        login_required(TableView.as_view(template_name="occupations.html")),
        name="occupations",
    )
]
