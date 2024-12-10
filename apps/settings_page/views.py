from django.views.generic import TemplateView

from account.models import Cashback
from web_project import TemplateLayout





class SettingsView(TemplateView):
    def get_context_data(self, **kwargs):
        # Global layoutni o'rnatish
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Cashback turini contextga qo'shish
        context["cashback_type_choices"] = Cashback.type_choices

        return context
