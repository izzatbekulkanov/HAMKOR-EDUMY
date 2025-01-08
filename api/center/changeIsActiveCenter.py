from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from center.models import Center
import json
from django.views import View


@csrf_exempt
def change_center_is_active(request, pk):
    if request.method == "POST":
        try:
            print(f"POST so'rovi qabul qilindi. PK: {pk}")  # Debug
            print(f"request.body: {request.body}")  # Debug

            try:
                center = Center.objects.get(pk=pk)
                print(f"Topilgan center: {center}")  # Debug
            except Center.DoesNotExist:
                print(f"Center topilmadi: PK = {pk}")  # Debug
                return JsonResponse({"success": False, "message": "Markaz topilmadi."}, status=404)

            # Hozirgi holatni almashtirish
            center.is_verified = not center.is_verified
            center.save()

            print(f"Center saqlandi: is_verified = {center.is_verified}")  # Debug

            return JsonResponse({
                "success": True,
                "message": f"Faollik holati muvaffaqiyatli {('faol' if center.is_verified else 'noaktif')} holatga o'zgartirildi.",
                "is_verified": center.is_verified
            })
        except Exception as e:
            print(f"Xatolik yuz berdi: {e}")  # Debug
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    print("Noto'g'ri so'rov turi.")  # Debug
    return JsonResponse({"success": False, "message": "Faqat POST so'rovi qabul qilinadi."}, status=400)


class ToggleCenterAllViews(View):
    def post(self, request, center_id):
        try:
            center = Center.objects.get(pk=center_id)
            center.all_views = not center.all_views  # Agar `True` bo'lsa, `False` qiladi va aksincha
            center.save()

            # Xabarni tayyorlash
            if center.all_views:
                message = "Endi barchaga ko'rinadi"
            else:
                message = "Endi barchaga ko'rinmaydi"

            return JsonResponse({"success": True, "all_views": center.all_views, "message": message})
        except Center.DoesNotExist:
            return JsonResponse({"success": False, "message": "Center topilmadi."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

