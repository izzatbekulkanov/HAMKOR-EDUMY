from django.conf import settings
from django.urls import path

from api.center.addCenter import AddCenterView
from api.center.addFillial import AddFilialView
from api.center.changeIsActiveCenter import change_center_is_active, ToggleCenterAllViews
from api.center.fetchSchool import FetchSchoolsView, AssignSchoolToCenterView, UnassignSchoolFromCenterView
from api.center.getCenter import GetCentersWithFilialsView, GetCenterDetailsView, GetCentersForTeacherView
from api.center.groups import GroupListView, KursFilterView, YonalishFilterView, KasbFilterView, toggle_group_active
from api.center.occupations import KasbListView, KasbUpdateView, YonalishListView, KursListView, GetKasbAndYonalishView
from api.center.statistics import StatisticsDashboardView
from api.center.teacher import submit_student
from api.location.get_location import get_districts, get_quarters
from api.schools.classes import StatsClassAPIView, add_class
from api.schools.schools import list_schools, add_school, delete_school, analyze_json_file, \
    bulk_add_schools, get_schools_by
from api.settings.cashback import AddCashbackAPIView, CashbackListAPIView, UserTypeAPIView
from api.settings.log import UserActivityLogView
from api.settings.regions import LocationAPIView, GetLocationsView
from api.settings.role import SaveRolesView, RolesWithUsersView
from api.user.addAdministrator import AddAdministratorView
from api.user.getAdministrator import GetAdministratorsView, GetAdminsView
from api.user.updateAdministrator import UpdateActivityView
from api.user.updateUserPhoto import update_user_photo

role_patterns = [
    path('save-roles/', SaveRolesView.as_view(), name='save_roles'),
    path('roles-with-users/', RolesWithUsersView.as_view(), name='roles_with_users'),
    path('user-activity-logs/', UserActivityLogView.as_view(), name='user_activity_logs'),
]

location_patterns = [
    path('get-districts/<int:region_id>/', get_districts, name='get_districts'),
    path('get-quarters/<int:district_id>/', get_quarters, name='get_quarters'),
]

user_patterns = [
    path('add-administrator/', AddAdministratorView.as_view(), name='add_administrator'),
    path('get-ceo-administrators/', GetAdministratorsView.as_view(), name='get_ceo_administrators'),
    path('update-activity/<int:admin_id>/', UpdateActivityView.as_view(), name='update_activity'),
    path('get-admins/', GetAdminsView.as_view(), name='get_admins'),
    path('cashbacks/add/', AddCashbackAPIView.as_view(), name='add-cashback'),
    path('cashbacks/list/', CashbackListAPIView.as_view(), name='list-cashback'),
    path('user-types/', UserTypeAPIView.as_view(), name='user-types'),
    path("update-user-photo/", update_user_photo, name="update_user_photo"),

]

center_patterns = [
    path('add-center/', AddCenterView.as_view(), name='add_center'),
    path('get-centers/', GetCentersWithFilialsView.as_view(), name='get-centers'),
    path('get-centers-teacher/', GetCentersForTeacherView.as_view(), name='get-centers'),
    path('get-center-details/<int:center_id>/', GetCenterDetailsView.as_view(), name='get-center-details'),
    path("add-filial/<int:center_id>/", AddFilialView.as_view(), name="add-filial"),
    path('kasblar/', KasbListView.as_view(), name='kasb_list_create'),
    path('kasblar/<int:kasb_id>/', KasbUpdateView.as_view(), name='kasb_update'),
    path('yonalishlar/', YonalishListView.as_view(), name='yonalish_list_create'),
    path('kurslar/', KursListView.as_view(), name='kurs_list_create'),
    path('filter-kasblar/', KasbFilterView.as_view(), name='kasb_list'),
    path('filter-yonalishlar/', YonalishFilterView.as_view(), name='yonalish_list'),
    path('filter-kurslar/', KursFilterView.as_view(), name='kurs_list'),
    path('groups/', GroupListView.as_view(), name='group_list'),
    path('statistics/', StatisticsDashboardView.as_view(), name='statistics_dashboard'),

    path('get-kasb-yonalish/', GetKasbAndYonalishView.as_view(), name='get-kasb-yonalish'),

    path("change-center-is-active/<int:pk>/", change_center_is_active, name="change-center-is-active"),

    path("fetch-schools/", FetchSchoolsView.as_view(), name="fetch-schools"),
    path("assign-school-to-center/", AssignSchoolToCenterView.as_view(), name="assign-school-to-center"),
    path("unassign-school-from-center/", UnassignSchoolFromCenterView.as_view(), name="unassign-school-from-center"),
    path("toggle-center-all-views/<int:center_id>/", ToggleCenterAllViews.as_view(), name="toggle-center-all-views"),


    path('groups/<int:group_id>/toggle-active/', toggle_group_active, name='toggle_group_active'),

]

schools_patterns = [
# API endpoints
    path("schools/", list_schools, name="list_schools"),  # Maktablar ro'yxati
    path("schools/add/", add_school, name="add_school"),  # Yangi maktab qo'shish
    path("schools/delete/<int:school_id>/", delete_school, name="delete_school"),  # Maktabni o'chirish
    path("schools/analyze/", analyze_json_file, name="analyze_json_file"),
    path("schools/bulk-add/", bulk_add_schools, name="save_json_file"),
    path('schools/grouped/', get_schools_by, name='get_schools_by'),
    path('classes/add/', add_class, name='add_class'),
    path('classes/stats/', StatsClassAPIView.as_view(), name='classes-stats-api'),
]

settings_patterns = [
    path('setting_locations/', LocationAPIView.as_view(), name='locations-api'),
    path('get-locations/', GetLocationsView.as_view(), name='get_locations'),
]

teacher_patterns = [
    path('submit-student/', submit_student, name='submit_student'),
]
urlpatterns = role_patterns + location_patterns + user_patterns + center_patterns + schools_patterns + settings_patterns + teacher_patterns
