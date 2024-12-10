from django.urls import path
from django.contrib.auth.views import LogoutView
from .login.views import LoginView, DjangoAuthLoginView
from .register.views import RegisterView

urlpatterns = [
    path("login/", LoginView.as_view(template_name="auth/login.html"), name="login"),

    path("register/", LoginView.as_view(template_name="auth/register.html"), name="register"),

    ##REST API
    path("api/login/", DjangoAuthLoginView.as_view(), name="DRF_login"),
    path("api/register/", RegisterView.as_view(), name="api_register"),

    path("logout/",LogoutView.as_view(),name="logout"),

]
