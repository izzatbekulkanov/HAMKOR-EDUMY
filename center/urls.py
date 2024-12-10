from django.urls import path

from config.decorators import verified_required
from .views import CenterView, FilialDetailUpdateView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "course/",
        verified_required(CenterView.as_view(template_name="course.html")),
        name="course",
    ),
    path(
        "learning-center/",
        verified_required(CenterView.as_view(template_name="learning_center.html")),
        name="learning-center",
    ),
    path(
        "learning-groups/",
        verified_required(CenterView.as_view(template_name="learning_groups.html")),
        name="learning-groups",
    ),
    path(
        "learning-statistics/",
        verified_required(CenterView.as_view(template_name="learning_statistics.html")),
        name="learning-statistics",
    ),
    path(
        "occupations/",
        verified_required(CenterView.as_view(template_name="occupations.html")),
        name="occupations",
    ),
    path(
        "accept_students/",
        verified_required(CenterView.as_view(template_name="accept_students.html")),
        name="accept-students",
    ),
    path(
        "teacher_cashback/",
        verified_required(CenterView.as_view(template_name="teacher/cashback.html")),
        name="teacher-cashback",
    ),
    path(
        "teacher_send_student/",
        verified_required(CenterView.as_view(template_name="teacher/send_students.html")),
        name="teacher-send-student",
    ),
    path(
        "bonus/",
        verified_required(CenterView.as_view(template_name="teacher/bonus.html")),
        name="teacher-send-bonus",
    ),
    # New URL pattern for Filial Detail View
    path(
        "filial-detail/<int:pk>/",  # The `pk` will be passed to the FilialDetailView
        verified_required(FilialDetailUpdateView.as_view(template_name="fillial_details.html")),
        name="filial-detail",
    ),
]
