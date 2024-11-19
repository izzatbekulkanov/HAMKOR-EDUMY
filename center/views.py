from django.views.generic import TemplateView

from center.models import Center
from web_project import TemplateLayout


class CenterView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Center modelining barcha ma'lumotlarini olish
        centers = Center.objects.all()

        # Ma'lumotlarni context ga qo'shish
        context['centers'] = centers

        return context


