from django.urls import path
from .views import CenterView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "course/",
        login_required(CenterView.as_view(template_name="course.html")),
        name="course",
    ),
    path(
        "learning-center/",
        login_required(CenterView.as_view(template_name="learning_center.html")),
        name="learning-center",
    ),
    path(
        "learning-groups/",
        login_required(CenterView.as_view(template_name="learning_groups.html")),
        name="learning-groups",
    ),
    path(
        "learning-statistics/",
        login_required(CenterView.as_view(template_name="learning_statistics.html")),
        name="learning-statistics",
    ),
    path(
        "occupations/",
        login_required(CenterView.as_view(template_name="occupations.html")),
        name="occupations",
    )
]
