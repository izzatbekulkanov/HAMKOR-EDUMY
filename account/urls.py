from django.urls import path
from .views import UsersView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "student/list/",
        login_required(UsersView.as_view(template_name="student_list.html")),
        name="student-list",
    ),path(
        "employee/list/",
        login_required(UsersView.as_view(template_name="employee_list.html")),
        name="employee-list",
    ),
    path(
        "user/view/account/",
        login_required(UsersView.as_view(template_name="view_account.html")),
        name="app-user-view-account",
    ),
    path(
        "user/view/security/",
        login_required(UsersView.as_view(template_name="view_security.html")),
        name="app-user-view-security",
    ),
    path(
        "user/view/billing/",
        login_required(UsersView.as_view(template_name="view_billing.html")),
        name="app-user-view-billing",
    ),
    path(
        "user/view/notifications/",
        login_required(UsersView.as_view(template_name="view_notifications.html")),
        name="user-view-notifications",
    ),
    path(
        "user/view/connections/",
        login_required(UsersView.as_view(template_name="user_view_connections.html")),
        name="user-view-connections",
    ),
]
