from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.contrib.auth.mixins import PermissionRequiredMixin


class UsersView(TemplateView):

    # Oldindan belgilangan funksiya
    def get_context_data(self, **kwargs):
        # Global layoutni boshlash uchun funksiya. Bu web_project/__init__.py faylida aniqlangan
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context
