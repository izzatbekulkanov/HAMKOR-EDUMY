from django.urls import path
from .views import LandingView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path( "", (LandingView.as_view(template_name="index.html")), name="index",)
]
