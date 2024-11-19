from django.http import JsonResponse
from django.views import View
from account.models import CustomUser
from center.models import Center

class AddCenterView(View):
    def post(self, request, *args, **kwargs):
        try:
            center_name = request.POST.get('centerName')
            admin_id = request.POST.get('centerAdmin')

            if not center_name or not admin_id:
                return JsonResponse({'success': False, 'message': 'Ma‘lumotlar to‘liq emas.'})

            admin = CustomUser.objects.get(id=admin_id)
            center = Center.objects.create(nomi=center_name, rahbari=admin)

            return JsonResponse({'success': True, 'message': 'O‘quv markaz muvaffaqiyatli qo‘shildi!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
