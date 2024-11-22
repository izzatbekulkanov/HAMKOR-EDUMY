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

        # Hamkor maktablar ro'yxati
        context['schools'] = [
            {
                "id": 1,
                "name": "Toshkent Maktabi",
                "description": "Toshkent maktabi yuqori sifatli ta'lim berish, xalqaro yondashuvni taklif etishi bilan tanilgan.",
                "image_url": "/static/images/school1.jpg",
            },
            {
                "id": 2,
                "name": "Namangan Litseyi",
                "description": "Namangan litseyi har bir talabaga individual yondashuvni taqdim etadi va yuqori natijalarga erishmoqda.",
                "image_url": "/static/images/school2.jpg",
            },
            {
                "id": 3,
                "name": "Andijon Akademiyasi",
                "description": "Andijon Akademiyasi xalqaro standartlarga mos keladigan ta'lim dasturini amalga oshiradi.",
                "image_url": "/static/images/school3.jpg",
            },
            {
                "id": 4,
                "name": "Buxoro Kolleji",
                "description": "Buxoro kollejida talabalar innovatsion texnologiyalardan foydalangan holda ta'lim olishadi.",
                "image_url": "/static/images/school4.jpg",
            },
            {
                "id": 5,
                "name": "Samarqand Litseyi",
                "description": "Samarqand litseyi ilmiy yutuqlarga yo'naltirilgan yuqori sifatli ta'lim dasturini taklif etadi.",
                "image_url": "/static/images/school5.jpg",
            },
        ]

        return context
