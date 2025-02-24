from django.views import View
from django.http import JsonResponse
from account.models import Cashback, CustomUser
from django.forms.models import model_to_dict

from center.models import Center
from config.send_telegram import send_telegram_message


# ✅ Cashback API View
class AddCashbackAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            # 📌 Ma'lumotlarni olish
            data = {key: request.POST.get(key, "").strip() for key in [
                "name", "summasi", "type", "user_type", "parent_summasi", "percentage", "parent_percentage"
            ]}

            # 📌 Majburiy maydonlarni tekshirish
            if not all([data["name"], data["type"], data["user_type"]]) or not (
                    data["summasi"] or data["parent_summasi"]):
                return JsonResponse({'success': False,
                                     'message': "Majburiy maydonlarni to‘ldiring! (summasi yoki parent_summasi bo‘lishi kerak)"},
                                    status=400)

            # 📌 Raqamli qiymatlarni tekshirish
            try:
                data["summasi"] = int(data["summasi"]) if data["summasi"] else 0
                data["parent_summasi"] = int(data["parent_summasi"]) if data["parent_summasi"] else 0
                data["percentage"] = float(data["percentage"]) if data["percentage"] else 0.0
                data["parent_percentage"] = float(data["parent_percentage"]) if data["parent_percentage"] else 0.0
            except ValueError:
                return JsonResponse({'success': False, 'message': "Summalar va foizlar noto‘g‘ri formatda!"},
                                    status=400)

            # 📌 Foydalanuvchi markazini olish
            center = Center.objects.filter(rahbari=request.user).first()
            if not center:
                return JsonResponse({'success': False, 'message': "Sizga birikkan markaz topilmadi."}, status=404)

            # 📌 Cashback yaratish yoki yangilash
            cashback, created = Cashback.objects.update_or_create(
                type=data["type"],
                user_type=data["user_type"],
                center=center,
                defaults={
                    "name": data["name"],
                    "summasi": data["summasi"],
                    "parent_summ": data["parent_summasi"],
                    "percentage": data["percentage"],
                    "parent_percentage": data["parent_percentage"],
                    "is_active": True
                }
            )

            # 📌 Telegram xabari
            message = f"📢 {'Yangi' if created else 'Yangilangan'} Cashback:\n\n" \
                      f"🏷 Nomi: {data['name']}\n" \
                      f"💰 Summasi: {data['summasi']:,} so‘m\n" \
                      f"💵 Foiz: {data['percentage']}%\n" \
                      f"👨‍👩‍👧 Ota-ona foizi: {data['parent_percentage']}%\n" \
                      f"🏢 Markaz: {center.nomi}"

            send_telegram_message(message)

            return JsonResponse({
                'success': True,
                'message': "Cashback muvaffaqiyatli qo‘shildi!" if created else "Cashback yangilandi!",
                'cashback': model_to_dict(cashback)
            })

        except Exception as e:
            print(f"❌ Xatolik: {e}")
            return JsonResponse({'success': False, 'message': "Server xatosi!"}, status=500)


class CashbackListAPIView(View):
    def get(self, request, *args, **kwargs):
        try:
            print("GET so'rovi qabul qilindi.")  # Debug
            print(f"Foydalanuvchi: {request.user}, Superuser: {request.user.is_superuser}")  # Debug

            # Superuser uchun barcha cashbacklarni olish
            if request.user.is_superuser:
                cashbacks = Cashback.objects.all()
                print(f"Barcha cashbacklar ({cashbacks.count()} ta) olindi.")  # Debug
            else:
                # Oddiy foydalanuvchilar uchun markazlar bilan bog‘liq cashbacklar
                user_centers = (
                        Center.objects.filter(rahbari=request.user) |
                        Center.objects.filter(maktab__customuser=request.user)
                )
                print(f"Foydalanuvchiga tegishli markazlar: {user_centers.count()} ta.")  # Debug

                cashbacks = Cashback.objects.filter(center__in=user_centers).distinct()
                print(f"Foydalanuvchiga tegishli cashbacklar: {cashbacks.count()} ta.")  # Debug

            cashback_data = []
            for cashback in cashbacks:
                print(f"Cashback ID: {cashback.id}, Nomi: {cashback.name}")  # Debug

                # Foydalanuvchilarni cashback va user_type bo'yicha filtrlash
                users = CustomUser.objects.filter(user_type=cashback.user_type, cashback__id=cashback.id)
                print(f"Cashbackga tegishli foydalanuvchilar soni: {users.count()}")  # Debug

                user_list = [
                    {
                        "full_name": f"{user.first_name} {user.second_name}",
                        "email": user.email or ""
                    }
                    for user in users
                ]
                print(f"Foydalanuvchilar ro‘yxati: {user_list}")  # Debug

                cashback_data.append({
                    "id": cashback.id,
                    "name": cashback.name,
                    "summasi": cashback.summasi,
                    "percentage": cashback.percentage,  # Foiz (%) qo‘shildi
                    "parent_sum": cashback.parent_summ,
                    "parent_percentage": cashback.parent_percentage,  # Ota-ona foizi qo‘shildi
                    "type": cashback.get_type_display(),
                    "user_type": cashback.get_user_type_display(),
                    "is_active": cashback.is_active,
                    "created_at": cashback.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "users": user_list,
                })

            print(f"Yakuniy cashback ma'lumotlari: {cashback_data}")  # Debug
            return JsonResponse({"success": True, "cashbacks": cashback_data}, status=200)

        except Exception as e:
            print(f"Xatolik yuz berdi: {str(e)}")  # Debug
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


class UserTypeAPIView(View):
    def get(self, request, *args, **kwargs):
        try:
            user_types = [
                {"value": choice[0], "label": choice[1]}
                for choice in CustomUser.type_choice
                if choice[0] not in ["4", "5"]  # Excluding Administrator and CEO_Administrator
            ]
            return JsonResponse({"success": True, "user_types": user_types})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)
