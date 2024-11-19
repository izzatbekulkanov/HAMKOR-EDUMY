from django.http import JsonResponse
from django.views import View
from center.models import Center, Filial


class AddFilialView(View):
    def post(self, request, center_id, *args, **kwargs):
        try:
            center = Center.objects.get(id=center_id)
            location = request.POST.get("location")
            contact = request.POST.get("contact")
            telegram = request.POST.get("telegram")
            image = request.FILES.get("image")

            filial = Filial.objects.create(
                center=center,
                location=location,
                contact=contact,
                telegram=telegram,
                image=image,
            )
            return JsonResponse({"success": True, "message": "Filial muvaffaqiyatli qo'shildi."})
        except Center.DoesNotExist:
            return JsonResponse({"success": False, "message": "O'quv markazi topilmadi."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)
