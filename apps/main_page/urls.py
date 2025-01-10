from django.urls import path

from config.decorators import verified_required
from .views import MainView, clear_toastr_session, SettingView, TeacherView

urlpatterns = [
    path(
        "student/",
        verified_required(MainView.as_view(template_name="student.html")),
        name="main-student",
    ),
    path(
        "administration/",
        verified_required(MainView.as_view(template_name="administrator.html")),
        name="main-administrator",
    ),
    path(
        "manager/",
        verified_required(MainView.as_view(template_name="manager.html")),
        name="main-manager",
    ),
    path(
        "teacher/",
        verified_required(TeacherView.as_view(template_name="teacher.html")),
        name="main-teacher",
    ),
    path(
        "director/",
        verified_required(MainView.as_view(template_name="director.html")),
        name="main-director",
    ),
    path(
        "",
        verified_required(MainView.as_view(template_name="main_page.html")),
        name="main-page-administrator",
    ),
    path(
        "waiting/",
        MainView.as_view(template_name="waiting.html"),
        name="waiting",
    ),
    path(
        "validate-add-user/",
        MainView.as_view(template_name="add_user_validate.html"),
        name="validate-add-user",
    ),
    path(
        "site-setting-administrator/",
        SettingView.as_view(template_name="site_settings.html"),
        name="site-setting-administrator",
    ),
    path('clear-toastr-session/', clear_toastr_session, name='clear_toastr_session')
]
