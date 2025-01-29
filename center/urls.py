from django.urls import path

from center.views.center import CenterView, CenterDetailView
from center.views.course import CoursesView
from center.views.egroups import LearningGroupView, add_or_remove_day
from center.views.fillial import FilialDetailUpdateView
from center.views.lines import LinesView, LinesDetailView
from center.views.occupation import OccupationsView, OccupationsDetailView
from config.decorators import verified_required
from center.views.student import StudentView, AddGroupStudentView, PayStudentView, BlockStudentView, \
    StatisticsStudentView, get_groups, add_payment
from center.views.teacher import TeacherView, TeacherCashbackView

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
    path('groups/<int:group_id>/add_or_remove_day/', add_or_remove_day, name='add_or_remove_day'),
    path("groups/<int:pk>/delete/",verified_required(LearningGroupView.as_view(template_name="learning_groups.html")), name="learning-delete_group"),

    path("learning-courses/", verified_required(CoursesView.as_view(template_name="courses.html")),name="learning-courses"),
    path("learning-courses/<int:pk>/edit/", verified_required(CoursesView.as_view(template_name="courses.html")),name="learning-courses"),
    path("learning-courses/<int:pk>/delete/", verified_required(CoursesView.as_view(template_name="courses.html")),name="learning-courses"),

    path("teacher_cashback/", verified_required(TeacherCashbackView.as_view(template_name="teacher/cashback.html")), name="teacher-cashback"),
    path("teacher_send_student/", verified_required(TeacherView.as_view(template_name="teacher/send_students.html")), name="teacher-send-student" ),
    path("teacher_students_list/", verified_required(TeacherView.as_view(template_name="teacher/students_list.html")), name="teacher-student-list" ),

    path("accept_students/", verified_required(StudentView.as_view(template_name="students/accept_students.html")),name="accept-students"),
    path("add_group_students/", verified_required(AddGroupStudentView.as_view(template_name="students/add-group-students.html")),name="add-group-students"),
    path("pay_students/", verified_required(PayStudentView.as_view(template_name="students/pay-student.html")),name="pay-students"),
    path("add_payment/", add_payment, name="add-payment"),
    path("block_students/", verified_required(BlockStudentView.as_view(template_name="students/block-student.html")),name="block-students"),
    path("statistics_students/", verified_required(StatisticsStudentView.as_view(template_name="students/statistics-student.html")),name="statistics-students"),

    path('get-groups/', get_groups, name='get_groups'),

    # New URL pattern for Filial Detail View
    path("filial-detail/<int:pk>/", verified_required(FilialDetailUpdateView.as_view(template_name="fillial_details.html")), name="filial-detail" ),
    path("center-detail/<int:pk>/", verified_required(CenterDetailView.as_view(template_name="center_detail.html")), name="center-detail" ),
]
