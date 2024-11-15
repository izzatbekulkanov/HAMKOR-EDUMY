from django.contrib import admin
from django.urls import include, path
from web_project.views import SystemView
from django.conf import settings
from django.conf.urls.static import static

main_urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("account.urls")),
    path("school/", include("school.urls")),
    path("learning/", include("center.urls")),
    path("users/", include("account.urls")),
    path("api/", include("api.urls")),


]

page_urlpatterns = [
    path("setting/", include("apps.settings_page.urls")),
    path("landing/", include("apps.landing_page.urls")),
    path("main/", include("apps.main_page.urls")),
    path("user/", include("apps.user_page.urls")),
]
other_urlpatterns = [
    # Dashboard urls
    path("", include("other.dashboards.urls")),

    # layouts urls
    path("", include("other.layouts.urls")),

    # FrontPages urls
    path("", include("other.front_pages.urls")),

    # FrontPages urls
    path("", include("other.mail.urls")),

    # Chat urls
    path("", include("other.chat.urls")),

    # Calendar urls
    path("", include("other.my_calendar.urls")),

    # kanban urls
    path("", include("other.kanban.urls")),

    # eCommerce urls
    path("", include("other.ecommerce.urls")),

    # Academy urls
    path("", include("other.academy.urls")),

    # Logistics urls
    path("", include("other.logistics.urls")),

    # Invoice urls
    path("", include("other.invoice.urls")),

    # User urls
    path("", include("other.users.urls")),

    # Access urls
    path("", include("other.access.urls")),

    # Pages urls
    path("", include("other.pages.urls")),

    # Auth urls
    path("", include("other.authentication.urls")),

    # Wizard urls
    path("", include("other.wizard_examples.urls")),

    # ModalExample urls
    path("", include("other.modal_examples.urls")),

    # Card urls
    path("", include("other.cards.urls")),

    # UI urls
    path("", include("other.ui.urls")),

    # Extended UI urls
    path("", include("other.extended_ui.urls")),

    # Icons urls
    path("", include("other.icons.urls")),

    # Forms urls
    path("", include("other.forms.urls")),

    # FormLayouts urls
    path("", include("other.form_layouts.urls")),

    # FormWizard urls
    path("", include("other.form_wizard.urls")),

    # FormValidation urls
    path("", include("other.form_validation.urls")),

    # Tables urls
    path("", include("other.tables.urls")),

    # Chart urls
    path("", include("other.charts.urls")),

    # Map urls
    path("", include("other.maps.urls")),

    # auth urls
    path("", include("auth.urls")),

    # transaction urls
    path("", include("other.transactions.urls")),
]
urlpatterns = main_urlpatterns + other_urlpatterns + page_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = SystemView.as_view(template_name="pages_misc_error.html", status=404)
handler403 = SystemView.as_view(template_name="pages_misc_not_authorized.html", status=403)
handler400 = SystemView.as_view(template_name="pages_misc_error.html", status=400)
handler500 = SystemView.as_view(template_name="pages_misc_error.html", status=500)
