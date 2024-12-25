from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.main_page.forms import SiteInfoForm, SeasonForm
from apps.main_page.models import SiteInfo, Season
from web_project import TemplateLayout
from django.shortcuts import render, redirect


class MainView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        cards_data = [
            {"title": "Foydalanuvchilar", "url_name": "user-administrator", "icon": "ti-users", "bg_color": "bg-primary", "text_color": "text-primary", "now_roles": ["5", "6"]},
            {"title": "O'quv markaz", "url_name": "learning-center", "icon": "ti-school", "bg_color": "bg-secondary", "text_color": "text-secondary", "now_roles": ["5", "6"]},
            {"title": "Kasblar", "url_name": "occupations", "icon": "ti-briefcase", "bg_color": "bg-success", "text_color": "text-success", "now_roles": ["4", "5"]},
            {"title": "Guruhlar", "url_name": "learning-groups", "icon": "ti-users-group", "bg_color": "bg-warning", "text_color": "text-warning", "now_roles": ["4", "5"]},
            {"title": "Hisobotlar", "url_name": "learning-statistics", "icon": "ti-file-report", "bg_color": "bg-danger", "text_color": "text-danger", "now_roles": ["6"]},
            {"title": "Qabul qilish", "url_name": "accept-students", "icon": "ti-heart-handshake", "bg_color": "bg-dark", "text_color": "text-dark", "now_roles": ["5", "4"]},
            {"title": "Maktablar", "url_name": "schools", "icon": "ti-building", "bg_color": "bg-primary", "text_color": "text-primary", "now_roles": ["6"]},
            {"title": "Sinflar", "url_name": "classes", "icon": "ti-books", "bg_color": "bg-info", "text_color": "text-info", "now_roles": ["5", "6"]},
            {"title": "Manzillar", "url_name": "setting-regions", "icon": "ti-map-pin", "bg_color": "bg-secondary", "text_color": "text-secondary", "now_roles": ["6"]},
            {"title": "Cashbeklar", "url_name": "setting-cashback", "icon": "ti-cash", "bg_color": "bg-success", "text_color": "text-success", "now_roles": ["5"]},
            {"title": "Loglar", "url_name": "setting-log", "icon": "ti-file-text", "bg_color": "bg-warning", "text_color": "text-warning", "now_roles": ["5", "6"]},
            {"title": "Rollar", "url_name": "setting-role", "icon": "ti-settings", "bg_color": "bg-danger", "text_color": "text-danger", "now_roles": ["6"]},

            # Role 2 uchun
            {"title": "O'quvchi yuborish", "url_name": "teacher-send-student", "icon": "ti-user-plus", "bg_color": "bg-primary", "text_color": "text-primary", "now_roles": ["2"]},
            {"title": "Yuborilgan o'quvchilar", "url_name": "teacher-student-list", "icon": "ti-list-check", "bg_color": "bg-success", "text_color": "text-success", "now_roles": ["2"]},
            {"title": "Keshbeklar", "url_name": "teacher-cashback", "icon": "ti-cash", "bg_color": "bg-warning", "text_color": "text-warning", "now_roles": ["2"]},
            {"title": "Mening sahifam", "url_name": "main-teacher", "icon": "ti-user-circle", "bg_color": "bg-info", "text_color": "text-info", "now_roles": ["2"]},
        ]
        context["cards_data"] = cards_data  # Kartalarni konteksga qo'shamiz
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

class SettingView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context = TemplateLayout.init(self, context)
        context["site_info"] = SiteInfo.objects.first()  # Fetch the first site info
        context["seasons"] = Season.objects.all()  # Fetch all seasons
        context["site_form"] = SiteInfoForm(
            instance=SiteInfo.objects.first()
        )  # Populate the form with existing site info
        context["season_form"] = SeasonForm()  # Empty form for adding a new season
        return context

    def post(self, request, *args, **kwargs):
        # Handle SiteInfo submission
        if "site_form" in request.POST:
            site_instance = SiteInfo.objects.first()
            site_form = SiteInfoForm(request.POST, instance=site_instance)

            if site_form.is_valid():
                site_form.save()
                return redirect("site-setting-administrator")
            else:
                return self.render_to_response(self.get_context_data(site_form=site_form))

        # Handle Season submission
        elif "season_form" in request.POST:
            season_name = request.POST.get("name")
            is_active = request.POST.get("is_active") == "on"
            season_instance = Season.objects.filter(name=season_name).first()

            if season_instance:
                season_form = SeasonForm(request.POST, instance=season_instance)
            else:
                season_form = SeasonForm(request.POST)

            if season_form.is_valid():
                if is_active:
                    # Deactivate all other seasons
                    Season.objects.update(is_active=False)
                season_form.save()
                return redirect("site-setting-administrator")
            else:
                return self.render_to_response(self.get_context_data(season_form=season_form))

        # Handle Season editing
        elif "edit_season_id" in request.POST:
            season_id = request.POST.get("edit_season_id")
            is_active = request.POST.get("is_active") == "on"
            season_instance = Season.objects.filter(id=season_id).first()
            if season_instance:
                if is_active:
                    # Deactivate all other seasons
                    Season.objects.exclude(id=season_id).update(is_active=False)
                season_instance.is_active = is_active
                season_instance.save()
                return redirect("site-setting-administrator")

        # Handle Season deletion
        elif "delete_season_id" in request.POST:
            season_id = request.POST.get("delete_season_id")
            season_instance = Season.objects.filter(id=season_id).first()
            if season_instance:
                season_instance.delete()
                return redirect("site-setting-administrator")

        # Default response
        return self.render_to_response(self.get_context_data())


