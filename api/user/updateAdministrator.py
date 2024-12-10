from django.http import JsonResponse
from django.views import View
from account.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

@method_decorator(csrf_exempt, name='dispatch')
class UpdateActivityView(View):
    def post(self, request, admin_id, *args, **kwargs):
        try:
            # JSON ma'lumotlarni o'qish
            data = json.loads(request.body)
            is_verified = data.get('is_verified')

            if is_verified is None:
                return JsonResponse({'success': False, 'message': 'Faollik holati ko‘rsatilmagan.'}, status=400)

            # Foydalanuvchini olish
            try:
                admin = CustomUser.objects.get(id=admin_id)
            except CustomUser.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Administrator topilmadi.'}, status=404)

            # Faollik holatini o‘zgartirish
            admin.is_verified = is_verified
            admin.save()

            return JsonResponse({'success': True, 'message': 'Faollik holati muvaffaqiyatli yangilandi.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Yaroqsiz JSON format.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Xatolik yuz berdi: {str(e)}'}, status=500)
