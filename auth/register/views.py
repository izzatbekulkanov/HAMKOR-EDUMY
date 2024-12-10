from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from account.models import Regions, District, Roles, Gender
from school.models import Maktab
from django.shortcuts import redirect
User = get_user_model()  # CustomUser modelini olish


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)  # JSON ma'lumotlarini o'qish

            print("Kiritilgan ma'lumotlar:", data)

            # Foydalanuvchidan kelgan ma'lumotlarni olish
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            phone_number_raw = data.get("phone_number")
            phone_number = phone_number_raw.replace(" ", "").replace("+", "")
            email = f"{phone_number}@info.uz"
            password = data.get("password")
            region = data.get("region")
            district = data.get("district")
            school_id = data.get("school")

            print(f"Ism: {first_name}, Familiya: {last_name}, Telefon: {phone_number}")
            print(f"Email: {email}, Parol: {password}, Viloyat: {region}, Tuman: {district}, Maktab ID: {school_id}")

            # Parol tasdiqlashni serverda tekshirish
            if not all([first_name, last_name, phone_number_raw, password]):
                print("Xatolik: Barcha maydonlar to'ldirilmagan.")
                return JsonResponse({"error": "Ism, familiya, telefon raqami va parol majburiy."}, status=400)

            # Telefon raqami bo'yicha foydalanuvchini tekshirish
            if User.objects.filter(phone_number=phone_number_raw).exists():
                print(f"Xatolik: Telefon raqami ({phone_number_raw}) allaqachon mavjud.")
                return JsonResponse({"error": "Bu telefon raqami bilan foydalanuvchi allaqachon mavjud."}, status=400)

            # Region, district va maktab obyektlarini olish
            region_obj = Regions.objects.filter(name=region).first()
            district_obj = District.objects.filter(name=district).first()
            school_obj = Maktab.objects.filter(id=school_id).first()

            # Familiya bo'yicha jinsni aniqlash
            gender_name = "Ayol" if last_name.lower().endswith("va") else "Erkak"
            gender_obj = Gender.objects.filter(name=gender_name).first()

            if not gender_obj:
                return JsonResponse({"error": f"{gender_name} jinsi mavjud emas."}, status=400)

            # Role modeli orqali "O'qituvchi" rolini olish
            teacher_role = Roles.objects.filter(code="2").first()
            if not teacher_role:
                return JsonResponse({"error": "O'qituvchi roli mavjud emas."}, status=400)

            # Foydalanuvchini yaratish
            print("Foydalanuvchi yaratilyapti...")
            user = User.objects.create_user(
                username=phone_number,
                email=email,
                first_name=first_name,
                second_name=last_name,
                phone_number=phone_number_raw,
                password=password,
                password_save=password,
                user_type="2",
                regions=region_obj,
                district=district_obj,
                maktab=school_obj,
                gender=gender_obj,
                now_role="2",
            )

            # Foydalanuvchiga "O'qituvchi" rolini bog'lash
            user.roles.add(teacher_role)
            user.save()
            print(f"Foydalanuvchi yaratildi va roli bog'landi: {user}")

            # Foydalanuvchini autentifikatsiya qilish
            authenticated_user = authenticate(username=phone_number, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                print("Foydalanuvchi tizimga kiritildi.")

                # Javobda redirect URL'ni qaytarish
                return JsonResponse({
                    "message": "Foydalanuvchi muvaffaqiyatli yaratildi.",
                    "redirect_url": reverse("main-page-administrator"),
                }, status=200)
            else:
                print("Xatolik: Autentifikatsiya amalga oshmadi.")
                return JsonResponse({"error": "Autentifikatsiya amalga oshmadi."}, status=400)

        except Exception as e:
            print("Server xatosi:", e)
            return JsonResponse({"error": f"Server xatosi: {str(e)}"}, status=500)


