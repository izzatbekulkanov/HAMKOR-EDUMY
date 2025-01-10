from django.views import View
from django.http import JsonResponse
from account.models import Cashback, CustomUser
from django.forms.models import model_to_dict

from center.models import Center


# Cashback yaratish uchun API
class AddCashbackAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get('name')
            summasi = request.POST.get('summasi')
            cashback_type = request.POST.get('type')
            user_type = request.POST.get('user_type')
            parent_summasi = request.POST.get('parent_summasi')

            if not all([name, summasi, cashback_type, user_type]):
                return JsonResponse({'success': False, 'message': 'Barcha maydonlarni to\'ldiring.'}, status=400)

            # Foydalanuvchi birikkan markazlarni topish
            user_centers = Center.objects.filter(rahbari=request.user)

            if not user_centers.exists():
                return JsonResponse({'success': False, 'message': 'Sizga birikkan markaz topilmadi.'}, status=404)

            # Birinchi markazni olish (agar bir nechta bo'lsa, tanlovni kengaytirish mumkin)
            center = user_centers.first()

            # Yangi cashback yaratishdan oldin mavjudligini tekshirish
            existing_cashback = Cashback.objects.filter(
                type=cashback_type,
                user_type=user_type,
                center=center
            ).first()

            if existing_cashback:
                # Agar cashback mavjud bo'lsa, uni yangilaymiz
                existing_cashback.name = name
                existing_cashback.summasi = summasi
                existing_cashback.parent_summ = parent_summasi
                existing_cashback.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Cashback mavjud edi va muvaffaqiyatli yangilandi!',
                    'cashback': model_to_dict(existing_cashback)
                })

            # Agar mavjud bo'lmasa, yangi cashback yaratamiz
            cashback = Cashback.objects.create(
                name=name,
                summasi=summasi,
                parent_summ=parent_summasi,
                type=cashback_type,
                user_type=user_type,
                center=center,  # Markazni biriktirish
                is_active=True
            )

            return JsonResponse({
                'success': True,
                'message': 'Cashback muvaffaqiyatli qo\'shildi!',
                'cashback': model_to_dict(cashback)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Xatolik yuz berdi: {str(e)}'}, status=500)



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
                    "parent_sum": cashback.parent_summ,
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
