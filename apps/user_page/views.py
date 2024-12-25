from datetime import datetime

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.hashers import make_password

from account.models import Roles, Regions, District, Quarters, CustomUser, Gender
from center.models import Center, Filial
from school.models import Maktab
from web_project import TemplateLayout


class UserAppView(TemplateView):

    def get_context_data(self, **kwargs):
        # Asosiy layoutni qo'shish
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Foydalanuvchi ma'lumotlarini olish
        user = self.request.user

        # Rollarni qo'shish
        if user.now_role == "6":
            context['roles'] = Roles.objects.all()
        else:
            excluded_roles = ["Administrator | CEO", "Hamkor", "Superadmin", "O'quvchi"]
            context['roles'] = Roles.objects.exclude(name__in=excluded_roles)

        # Viloyat, tuman va mahalla ma'lumotlarini qo'shish
        context['regions'] = Regions.objects.all()
        context['districts'] = District.objects.all()
        context['quarters'] = Quarters.objects.all()

        # Foydalanuvchilar soni va tasdiqlangan / tasdiqlanmaganlar sonini qo'shish
        if user.now_role == "6" or user.is_superuser:
            context['user_counts'] = {
                'students': CustomUser.objects.filter(user_type="1").count(),
                'teachers': CustomUser.objects.filter(user_type="2").count(),
                'directors': CustomUser.objects.filter(user_type="3").count(),
                'administrators': CustomUser.objects.filter(user_type="4").count(),
                'ceo_administrators': CustomUser.objects.filter(user_type="5").count(),
                'superadmins': CustomUser.objects.filter(user_type="6").count(),
                'verified': CustomUser.objects.filter(is_verified=True).count(),
                'unverified': CustomUser.objects.filter(is_verified=False).count()
            }

        # Agar foydalanuvchi rahbar bo'lsa, markazga bog'liq foydalanuvchilarni hisoblash
        elif user.now_role == "5" and user.user_type == "5":
            centers = Center.objects.filter(rahbari=user)
            filials = Filial.objects.filter(center__in=centers)
            related_users = CustomUser.objects.filter(
                Q(maktab__centers__in=centers) |  # Markazlarga birikkan maktablar orqali
                Q(maktab__in=Maktab.objects.filter(centers__in=centers)) |  # Maktablar markaz orqali
                Q(administered_filials__in=filials) |  # Filiallarga birikkan foydalanuvchilar
                Q(added_by=user)  # Foydalanuvchi tomonidan qo'shilganlar
            ).distinct()

            # Maktab ma'lumotlarini olish
            schools = Maktab.objects.filter(centers__in=centers).distinct()

            # Filial ma'lumotlarini olish
            branches = filials.distinct()

            context['user_counts'] = {
                'students': related_users.filter(user_type="1").count(),
                'teachers': CustomUser.objects.filter(user_type="2").count(),
                'directors': related_users.filter(user_type="3").count(),
                'administrators': related_users.filter(user_type="4").count(),
                'ceo_administrators': related_users.filter(user_type="5").count(),
                'superadmins': related_users.filter(user_type="6").count(),
                'verified': related_users.filter(is_verified=True).count(),
                'unverified': related_users.filter(is_verified=False).count(),
            }

            # Qo'shimcha ma'lumotlar (Maktab va filiallar)
            context['schools'] = [
                {
                    'id': school.id,
                    'viloyat': school.viloyat,
                    'tuman': school.tuman,
                    'nomi': school.nomi,
                    'maktab_raqami': school.maktab_raqami,
                }
                for school in schools
            ]

            context['branches'] = [
                {
                    'id': branch.id,
                    'location': branch.location,
                    'contact': branch.contact,
                    'center': branch.center.nomi if branch.center else "Markazsiz",
                }
                for branch in branches
            ]

        return context


class UserDetailView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        user_id = self.kwargs.get("pk")
        user = get_object_or_404(CustomUser, pk=user_id)

        request_user = self.request.user


        # Telefon raqamni +998 prefiksidan tozalash
        phone_number = user.phone_number
        if phone_number and phone_number.startswith("+998"):
            phone_number = phone_number[4:].strip()  # +998 ni olib tashlash

        type_choices = (
            CustomUser.type_choice if request_user.now_role == "6"
            else [choice for choice in CustomUser.type_choice if choice[0] in ["1", "2", "3", "4"]]
        )

            # Roles ni tekshirish
        if request_user.now_role == "6":
            roles = Roles.objects.all()
        else:
            roles = Roles.objects.exclude(code__in=["5", "6"])

        context["user"] = user
        context["roles"] = roles  # Filtrlangan rollarni qo'shish
        context["phone_number"] = phone_number  # Telefon raqamni konteksga yuborish
        context["birth_date"] = user.birth_date  # Tug‘ilgan sanani konteksga yuborish
        context["gender"] = user.gender  # Genderni konteksga yuborish
        context["type_choices"] = type_choices  # Filtrlangan type choice ma'lumotlari
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

        # Parolni yangilash

        new_password = request.POST.get("new_password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        print(new_password, confirm_password)

        if new_password or confirm_password:
            if new_password != confirm_password:
                messages.error(request, "Parollar mos emas!")
                return redirect("user-details", pk=user.pk)

            if len(new_password) < 6:
                messages.error(request, "Parol kamida 6 belgidan iborat bo'lishi kerak.")
                return redirect("user-details", pk=user.pk)

            # Save plain text password to `password_save`
            user.password_save = new_password

            # Save hashed password to `password`
            user.password = make_password(new_password)

        user.save()
        messages.success(request, "Foydalanuvchi muvaffaqiyatli saqlandi!")
        return redirect("user-details", pk=user.pk)
