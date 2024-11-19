from django.http import JsonResponse
from django.views import View
from account.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')  # CSRF muhofazasini o‘chirish
class UpdateActivityView(View):
    def post(self, request, admin_id, *args, **kwargs):
        try:
            # Ma'lumotni olish
            data = json.loads(request.body)
            is_active = data.get('is_active', None)

            if is_active is None:
                return JsonResponse({'success': False, 'message': 'Faollik holati ko‘rsatilmagan.'}, status=400)

            # Foydalanuvchini olish
            try:
                admin = CustomUser.objects.get(id=admin_id, user_type="5")
            except CustomUser.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Administrator topilmadi.'}, status=404)

            # Faollik holatini o‘zgartirish
            admin.is_active = is_active
            admin.save()

            return JsonResponse({'success': True, 'message': 'Faollik holati muvaffaqiyatli yangilandi.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Yaroqsiz JSON format.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Xatolik yuz berdi: {str(e)}'}, status=500)
