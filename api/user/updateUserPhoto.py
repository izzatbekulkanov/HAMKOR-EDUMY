from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from account.models import CustomUser

@csrf_exempt
def update_user_photo(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        image_file = request.FILES.get("imageFile")

        if not user_id or not image_file:
            return JsonResponse({"status": "error", "message": "Foydalanuvchi ID yoki rasm topilmadi."})

        try:
            user = get_object_or_404(CustomUser, id=user_id)
            user.imageFile = image_file
            user.save()
            return JsonResponse({"status": "success", "message": "Rasm muvaffaqiyatli yangilandi."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Xatolik yuz berdi: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Faqat POST so'rovlari qabul qilinadi."})
