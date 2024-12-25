from django.views.generic import TemplateView
from web_project import TemplateLayout
import traceback


class SystemView(TemplateView):
    status = None  # Default qiymat

    def dispatch(self, request, *args, **kwargs):
        try:
            print(f"Redirecting to template: {self.template_name}, Status Code: {self.status}")
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            print(f"Error while processing: {e}")
            traceback.print_exc()
            raise e

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['status'] = self.status
        return context
