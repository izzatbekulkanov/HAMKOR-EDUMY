from django.urls import path
from .views import SchoolView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path(
        "schools/",
        login_required(SchoolView.as_view(template_name="schools.html")),
        name="schools",
    ),
    path(
        "classes/",
        login_required(SchoolView.as_view(template_name="classes.html")),
        name="classes",
    )
]
