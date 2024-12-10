from django.urls import path

from config.decorators import verified_required
from .views import SchoolView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "schools/",
        verified_required(SchoolView.as_view(template_name="schools.html")),
        name="schools",
    ),
    path(
        "classes/",
        verified_required(SchoolView.as_view(template_name="classes.html")),
        name="classes",
    )
]
