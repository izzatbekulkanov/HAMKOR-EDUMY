from django.urls import path
from config.decorators import verified_required
from .views import CenterView, FilialDetailUpdateView, CenterDetailView


urlpatterns = [
    path("learning-center/", verified_required(CenterView.as_view(template_name="learning_center.html")),name="learning-center"),
    path("learning-groups/", verified_required(CenterView.as_view(template_name="learning_groups.html")),name="learning-groups"),
    path("learning-statistics/", verified_required(CenterView.as_view(template_name="learning_statistics.html")),name="learning-statistics" ),
    path("occupations/", verified_required(CenterView.as_view(template_name="occupations.html")), name="occupations" ),
    path("accept_students/", verified_required(CenterView.as_view(template_name="accept_students.html")), name="accept-students"),
    path("teacher_cashback/", verified_required(CenterView.as_view(template_name="teacher/cashback.html")), name="teacher-cashback"),
    path("teacher_send_student/", verified_required(CenterView.as_view(template_name="teacher/send_students.html")), name="teacher-send-student" ),
    path("teacher_students_list/", verified_required(CenterView.as_view(template_name="teacher/students_list.html")), name="teacher-student-list" ),
    # New URL pattern for Filial Detail View
    path("filial-detail/<int:pk>/", verified_required(FilialDetailUpdateView.as_view(template_name="fillial_details.html")), name="filial-detail" ),
    path("center-detail/<int:pk>/", verified_required(CenterDetailView.as_view(template_name="center_detail.html")), name="center-detail" ),
]
