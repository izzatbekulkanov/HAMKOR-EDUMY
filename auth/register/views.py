from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

from account.models import Regions, District, Roles, Gender, CashbackRecord, Cashback
from config.send_telegram import send_telegram_message
from school.models import Maktab
from django.shortcuts import redirect

User = get_user_model()  # CustomUser modelini olish


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
    def post(self, request, *args, **kwargs):
        try:
            # 📌 JSON ma'lumotlarini o‘qish
            data = json.loads(request.body)

            # 📌 Foydalanuvchi ma'lumotlarini olish
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            phone_number_raw = data.get("phone_number")
            phone_number = phone_number_raw.replace(" ", "").replace("+", "")
            email = f"{phone_number}@info.uz"
            password = data.get("password")
            region = data.get("region")
            district = data.get("district")
            school_id = data.get("school")

            # 📌 Majburiy maydonlarni tekshirish
            if not all([first_name, last_name, phone_number_raw, password]):
                return JsonResponse({"error": "Ism, familiya, telefon raqami va parol majburiy."}, status=400)

            # 📌 Telefon raqami bo‘yicha foydalanuvchini tekshirish
            if User.objects.filter(phone_number=phone_number_raw).exists():
                return JsonResponse({"error": "Bu telefon raqami bilan foydalanuvchi allaqachon mavjud."}, status=400)

            # 📌 Region, tuman va maktabni olish
            region_obj = Regions.objects.filter(name=region).first()
            district_obj = District.objects.filter(name=district).first()
            school_obj = Maktab.objects.filter(id=school_id).first()

            # 📌 Familiya bo‘yicha jinsni aniqlash
            gender_name = "Ayol" if last_name.lower().endswith("va") else "Erkak"
            gender_obj = Gender.objects.filter(name=gender_name).first()
            if not gender_obj:
                return JsonResponse({"error": f"{gender_name} jinsi mavjud emas."}, status=400)

            # 📌 "O‘qituvchi" rolini olish
            teacher_role = Roles.objects.filter(code="2").first()
            if not teacher_role:
                return JsonResponse({"error": "O‘qituvchi roli mavjud emas."}, status=400)

            # 📌 Ro‘yxatdan o‘tganlik uchun cashbackni olish
            cashback = Cashback.objects.filter(type="1").first()
            if not cashback:
                error_message = "🚨 Ro‘yxatdan o‘tganlik uchun cashback topilmadi!"
                send_telegram_message(error_message)  # 🔹 Telegramga xabar yuborish
                return JsonResponse({"error": error_message}, status=400)

            # ✅ Tranzaksiya ichida barcha jarayonlarni bajarish
            with transaction.atomic():
                # ✅ Foydalanuvchini yaratish
                user = User.objects.create_user(
                    username=phone_number,
                    email=email,
                    first_name=first_name,
                    second_name=last_name,
                    phone_number=phone_number_raw,
                    password=password,
                    password_save=password,
                    user_type="2",
                    maktab=school_obj,
                    gender=gender_obj,
                    now_role="2",
                )

                # ✅ "O‘qituvchi" rolini bog‘lash
                user.roles.add(teacher_role)
                user.save()

                # ✅ CashbackRecord yaratish
                cashback_record = CashbackRecord.objects.create(
                    cashback=cashback,
                    teacher=user,
                    student=None,  # Hozircha o‘quvchi yo‘q
                    is_viewed=False,
                    is_paid=False
                )

            # ✅ Telegramga xabar yuborish
            success_message = (
                f"🎉 Yangi foydalanuvchi ro‘yxatdan o‘tdi!\n\n"
                f"👤 Ism: {first_name} {last_name}\n"
                f"📞 Telefon: {phone_number_raw}\n"
                f"🏫 Maktab: {school_obj.nomi if school_obj else 'Noma’lum'}\n"
                f"💰 Cashback tayinlandi: {cashback.name}\n"
                f"🕒 Sana: {cashback_record.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            send_telegram_message(success_message)

            # ✅ Foydalanuvchini autentifikatsiya qilish
            authenticated_user = authenticate(username=phone_number, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                return JsonResponse({
                    "message": "Foydalanuvchi muvaffaqiyatli yaratildi.",
                    "redirect_url": reverse("main-page-administrator"),
                }, status=200)
            else:
                return JsonResponse({"error": "Autentifikatsiya amalga oshmadi."}, status=400)

        except Exception as e:
            error_message = f"🚨 Server xatosi: {str(e)}"
            send_telegram_message(error_message)  # 🔹 Xatolikni Telegramga yuborish
            return JsonResponse({"error": error_message}, status=500)