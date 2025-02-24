from django.views.generic import TemplateView

from web_project import TemplateLayout


class AddStudentCenterView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context