from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from pathlib import Path
from config.error_views import SystemView

BASE_DIR = Path(__file__).resolve().parent.parent

main_urlpatterns = [
    path("admin/", admin.site.urls),  # Admin uchun xatolik ishlovchilarni chetlash
    path("users/", include("account.urls")),
    path("school/", include("school.urls")),
    path("learning/", include("center.urls")),
    path("api/", include("api.urls")),
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
    # Static va Media fayllarni server orqali yetkazish
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=BASE_DIR / "src" / "assets")
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    from django.views.static import serve
    from django.urls import re_path

    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# Xatolik ishlovchilari faqat maxsus sahifalar uchun
handler404 = SystemView.as_view(template_name="pages_misc_error404.html", status=404)
handler403 = SystemView.as_view(template_name="pages_misc_not_authorized.html", status=403)
handler400 = SystemView.as_view(template_name="pages_misc_error400.html", status=400)
handler500 = SystemView.as_view(template_name="pages_misc_error500.html", status=500)
