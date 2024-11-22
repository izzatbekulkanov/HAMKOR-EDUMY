from django.views.generic import TemplateView

from account.models import Roles, Regions, District, Quarters
from web_project import TemplateLayout


class LandingView(TemplateView):
    # template_name = "add_administrator.html"

    def get_context_data(self, **kwargs):
        # Asosiy layoutni qo'shish
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Barcha rollar, viloyatlar, tumanlar va mahallalarni yuborish
        context['roles'] = Roles.objects.all()
        context['regions'] = Regions.objects.all()
        context['districts'] = District.objects.all()
        context['quarters'] = Quarters.objects.all()

        return context
