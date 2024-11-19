from django.views import View
from django.http import JsonResponse
from account.models import Cashback, CustomUser
from django.forms.models import model_to_dict


# Cashback yaratish uchun API
class AddCashbackAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            name = request.POST.get('name')
            summasi = request.POST.get('summasi')
            cashback_type = request.POST.get('type')
            user_type = request.POST.get('user_type')

            if not all([name, summasi, cashback_type, user_type]):
                return JsonResponse({'success': False, 'message': 'Barcha maydonlarni to\'ldiring.'}, status=400)

            cashback = Cashback.objects.create(
                name=name,
                summasi=summasi,
                type=cashback_type,
                user_type=user_type,
                is_active=True
            )
            return JsonResponse({'success': True, 'message': 'Cashback muvaffaqiyatli qo\'shildi!',
                                 'cashback': model_to_dict(cashback)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Xatolik yuz berdi: {str(e)}'}, status=500)


class CashbackListAPIView(View):
    def get(self, request, *args, **kwargs):
        try:
            cashbacks = Cashback.objects.all()
            cashback_data = []

            for cashback in cashbacks:
                # Foydalanuvchilarni user_type bo'yicha filtrlaymiz
                users = CustomUser.objects.filter(user_type=cashback.user_type)
                user_list = [{"full_name": user.get_full_name(), "email": user.email} for user in users]

                cashback_data.append({
                    "id": cashback.id,
                    "name": cashback.name,
                    "summasi": cashback.summasi,
                    "type": cashback.get_type_display(),
                    "user_type": cashback.get_user_type_display(),
                    "is_active": cashback.is_active,
                    "created_at": cashback.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "users": user_list,
                })

            return JsonResponse({"success": True, "cashbacks": cashback_data})
        except Exception as e:
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
