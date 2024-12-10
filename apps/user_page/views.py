from datetime import datetime

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from account.models import Roles, Regions, District, Quarters, CustomUser, Gender
from web_project import TemplateLayout


class UserAppView(TemplateView):
    template_name = "add_administrator.html"

    def get_context_data(self, **kwargs):
        # Asosiy layoutni qo'shish
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Foydalanuvchi ma'lumotlarini olish
        user = self.request.user

        # Agar foydalanuvchining now_role qiymati 6 bo'lsa, barcha rollarni ko'rsatish
        if user.now_role == "6":
            context['roles'] = Roles.objects.all()
        else:
            # Boshqa foydalanuvchilar uchun cheklangan rollar
            excluded_roles = ["Administrator | CEO", "Hamkor", "Superadmin"]
            context['roles'] = Roles.objects.exclude(name__in=excluded_roles)

        # Viloyat, tuman va mahalla ma'lumotlarini qo'shish
        context['regions'] = Regions.objects.all()
        context['districts'] = District.objects.all()
        context['quarters'] = Quarters.objects.all()

        return context


class UserDetailView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user_id = self.kwargs.get("pk")
        user = get_object_or_404(CustomUser, pk=user_id)

        # Telefon raqamni +998 prefiksidan tozalash
        phone_number = user.phone_number
        if phone_number and phone_number.startswith("+998"):
            phone_number = phone_number[4:].strip()  # +998 ni olib tashlash

        context["user"] = user
        context["roles"] = Roles.objects.all()  # Barcha rollarni qo'shish
        context["phone_number"] = phone_number  # Telefon raqamni konteksga yuborish
        context["birth_date"] = user.birth_date  # Tug‘ilgan sanani konteksga yuborish
        context["gender"] = user.gender  # Genderni konteksga yuborish
        context["type_choices"] = CustomUser.type_choice  # Type choice ma'lumotlari
        return context

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get("pk")
        user = get_object_or_404(CustomUser, pk=user_id)
        print(request.POST)

        # Foydalanuvchi ma'lumotlarini yangilash
        user.first_name = request.POST.get("first_name", user.first_name)
        user.second_name = request.POST.get("second_name", user.second_name)
        user.third_name = request.POST.get("third_name", user.third_name)

        # Telefon raqamni boshiga +998 qo‘shish
        phone_number = request.POST.get("phone_number", "").strip()
        if phone_number:
            if not phone_number.startswith("+998"):
                phone_number = f"+998{phone_number}"
            user.phone_number = phone_number

        user.email = request.POST.get("email", user.email)

        # Tug'ilgan sanani tekshirish va formatlash
        birth_date = request.POST.get("birth_date", "")
        if birth_date:  # Agar bo'sh bo'lmasa
            try:
                user.birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Noto‘g‘ri tug‘ilgan sana formati. YYYY-MM-DD formatida bo‘lishi kerak.")
                return redirect("user-details", pk=user.pk)
        else:
            user.birth_date = None

        # Foydalanuvchi rasm fayli
        if "imageFile" in request.FILES:
            user.imageFile = request.FILES["imageFile"]

        # Rollarni yangilash
        selected_roles = request.POST.getlist("roles")  # Checkboxlardan tanlangan rollar
        user.roles.set(selected_roles)  # Foydalanuvchi rollarini yangilash

        # Genderni aniqlash
        last_name = user.second_name  # Familiya (second_name)
        if last_name and last_name.endswith("v"):
            gender_name = "Erkak"
        elif last_name and last_name.endswith("a"):
            gender_name = "Ayol"
        else:
            gender_name = None

        if gender_name:
            # Gender mavjudmi, tekshirish
            gender, created = Gender.objects.get_or_create(name=gender_name)
            user.gender = gender  # Genderni foydalanuvchiga biriktirish
        else:
            user.gender = None

        # Type choice va now_role yangilash
        user_type = request.POST.get("type_choice", user.user_type)
        if user_type in dict(CustomUser.type_choice):
            user.user_type = user_type
            user.now_role = user_type  # now_role maydonini user_type ga tenglashtirish

        user.save()
        messages.success(request, "Foydalanuvchi muvaffaqiyatli saqlandi!")
        return redirect("user-details", pk=user.pk)
