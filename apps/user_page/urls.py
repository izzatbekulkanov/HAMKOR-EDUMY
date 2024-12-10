from django.urls import path

from config.decorators import verified_required
from .views import UserAppView, UserDetailView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path("users/", verified_required(UserAppView.as_view(template_name="users.html")), name="user-administrator",),
    path("addAdministrators/", verified_required(UserAppView.as_view(template_name="add_administrator.html")), name="addAdministrators",),
    path("manager/",  verified_required(UserAppView.as_view(template_name="manager.html")), name="user-menejer",),
    path("user-details/<int:pk>/", UserDetailView.as_view(template_name="user_details.html"), name="user-details"),

]
