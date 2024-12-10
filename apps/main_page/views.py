from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from web_project import TemplateLayout
from django.shortcuts import render



class TableView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


@csrf_exempt
def clear_toastr_session(request):
    """
    Toastr sessiya qiymatlarini tozalash.
    """
    if request.method == "POST":
        request.session.pop('show_login_toastr', None)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"}, status=400)
