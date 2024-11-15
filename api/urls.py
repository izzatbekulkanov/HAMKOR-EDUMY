from django.urls import path

from api.settings.log import UserActivityLogView
from api.settings.role import SaveRolesView, RolesWithUsersView

urlpatterns = [
    path('save-roles/', SaveRolesView.as_view(), name='save_roles'),
    path('roles-with-users/', RolesWithUsersView.as_view(), name='roles_with_users'),
    path('user-activity-logs/', UserActivityLogView.as_view(), name='user_activity_logs'),
]




