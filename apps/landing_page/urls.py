from django.urls import path
from .views import LandingView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path( "", (LandingView.as_view(template_name="landing_layout/main.html")), name="index",),
    path( "contact-me", (LandingView.as_view(template_name="landing_pages/contact_me.html")), name="contact_me",),
    path( "partner-schools", (LandingView.as_view(template_name="landing_pages/partner_schools.html")), name="partner_schools",),
]
