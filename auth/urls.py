from django.urls import path
from django.contrib.auth.views import LogoutView
from .login.views import LoginView, JWTAuthView



urlpatterns = [
    path("login/", LoginView.as_view(template_name="auth/login.html"), name="login"),

    ##REST API
    path("api/login/", JWTAuthView.as_view(), name="jwt_login"),

    path("logout/",LogoutView.as_view(),name="logout"),

]
