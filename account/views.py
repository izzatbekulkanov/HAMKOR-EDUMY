from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.contrib.auth.mixins import PermissionRequiredMixin

"""
Ushbu fayl modullangan bir nechta sahifalar uchun ko'rish nazoratchisi hisoblanadi.
Bu yerda sahifa ko'rinishini moslashtirish mumkin.
Qo'shimcha sahifalar uchun users/urls.py fayliga murojaat qiling.
"""


class UsersView(PermissionRequiredMixin, TemplateView):
    permission_required = ("user.view_user", "user.delete_user", "user.change_user", "user.add_user")

    # Oldindan belgilangan funksiya
    def get_context_data(self, **kwargs):
        # Global layoutni boshlash uchun funksiya. Bu web_project/__init__.py faylida aniqlangan
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context
