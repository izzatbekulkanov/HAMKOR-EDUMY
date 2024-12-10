from django.contrib import admin
from django.urls import include, path
from web_project.views import SystemView
from django.conf import settings
from django.conf.urls.static import static
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

main_urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("account.urls")),
    path("school/", include("school.urls")),
    path("learning/", include("center.urls")),
    path("api/", include("api.urls")),
    # auth urls
    path("", include("auth.urls")),


]

page_urlpatterns = [
    path("setting/", include("apps.settings_page.urls")),
    path("", include("apps.landing_page.urls")),
    path("main/", include("apps.main_page.urls")),
    path("user/", include("apps.user_page.urls")),
]
urlpatterns = main_urlpatterns + page_urlpatterns

if settings.DEBUG:
    # Static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=BASE_DIR / "src" / "assets")

    # Media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = SystemView.as_view(template_name="pages_misc_error.html", status=404)
handler403 = SystemView.as_view(template_name="pages_misc_not_authorized.html", status=403)
handler400 = SystemView.as_view(template_name="pages_misc_error.html", status=400)
handler500 = SystemView.as_view(template_name="pages_misc_error.html", status=500)
