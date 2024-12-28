from django.urls import path
from config.decorators import verified_required
from .views import CenterView, FilialDetailUpdateView, CenterDetailView, OccupationsView, OccupationsDetailView, \
    LinesView, CoursesView, LinesDetailView, LearningGroupView

urlpatterns = [
    path("learning-center/", verified_required(CenterView.as_view(template_name="learning_center.html")),name="learning-center"),
    path("learning-statistics/", verified_required(CenterView.as_view(template_name="learning_statistics.html")),name="learning-statistics" ),
    path("occupations/", verified_required(OccupationsView.as_view(template_name="occupations.html")), name="occupations" ),
    path("kasblar/delete/<int:pk>/", OccupationsView.as_view(), name="delete_kasb"),
    path("kasb/<int:pk>/", verified_required(OccupationsDetailView.as_view(template_name="occupations-detail.html")),name="occupations-detail"),

    path("learning-lines/", verified_required(LinesView.as_view(template_name="lines.html")),name="learning-lines"),
    path("lines-detail/<int:pk>/", verified_required(LinesDetailView.as_view(template_name="lines-detail.html")),name="lines-detail"),
    path('learning-lines/delete/<int:pk>/', LinesView.as_view(), name='learning-lines-delete'),

    path("learning-groups/", verified_required(LearningGroupView.as_view(template_name="learning_groups.html")),name="learning-groups"),
    path("learning-groups/<int:pk>/edit/", verified_required(LearningGroupView.as_view(template_name="learning_groups.html")),name="learning-groups"),

    path("learning-courses/", verified_required(CoursesView.as_view(template_name="courses.html")),name="learning-courses"),
    path("learning-courses/<int:pk>/edit/", verified_required(CoursesView.as_view(template_name="courses.html")),name="learning-courses"),
    path("learning-courses/<int:pk>/delete/", verified_required(CoursesView.as_view(template_name="courses.html")),name="learning-courses"),

    path("accept_students/", verified_required(CenterView.as_view(template_name="accept_students.html")), name="accept-students"),
    path("teacher_cashback/", verified_required(CenterView.as_view(template_name="teacher/cashback.html")), name="teacher-cashback"),
    path("teacher_send_student/", verified_required(CenterView.as_view(template_name="teacher/send_students.html")), name="teacher-send-student" ),
    path("teacher_students_list/", verified_required(CenterView.as_view(template_name="teacher/students_list.html")), name="teacher-student-list" ),
    # New URL pattern for Filial Detail View
    path("filial-detail/<int:pk>/", verified_required(FilialDetailUpdateView.as_view(template_name="fillial_details.html")), name="filial-detail" ),
    path("center-detail/<int:pk>/", verified_required(CenterDetailView.as_view(template_name="center_detail.html")), name="center-detail" ),
]
