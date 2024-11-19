from django.http import JsonResponse
from django.views import View
from center.models import Kasb, Yonalish, Kurs
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json


class KasbListView(View):
    """
    `Kasb` ob'yektlarini ro'yxatini olish va yangi kasb qo'shishni amalga oshiruvchi View.
    """

    def get(self, request, *args, **kwargs):
        """
        GET so'rovlar uchun `Kasb` ob'yektlari va ular bilan bog'liq sonlarni ro'yxatini qaytaradi.
        """
        kasblar = Kasb.objects.all().order_by('-created_at')
        data = [
            {
                "id": kasb.id,
                "nomi": kasb.nomi,
                "is_active": kasb.is_active,
                "yonalish_count": kasb.yonalishlar.count(),  # Yo'nalishlar soni
                "kurs_count": sum(yonalish.kurslar.count() for yonalish in kasb.yonalishlar.all()),  # Kurslar soni
                "guruh_count": sum(
                    kurs.groups.count() for yonalish in kasb.yonalishlar.all() for kurs in yonalish.kurslar.all()
                ),  # Guruhlar soni
            }
            for kasb in kasblar
        ]
        return JsonResponse({"success": True, "data": data})

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        """
        POST so'rovlar uchun yangi `Kasb` ob'yektini yaratadi.
        """
        if request.content_type != "application/json":
            return JsonResponse({"success": False, "message": "Noto'g'ri kontent turi. `application/json` bo'lishi kerak."},
                                status=400)

        try:
            data = json.loads(request.body.decode('utf-8'))  # So'rov tanasini dekodlash
            nomi = data.get("nomi")
            if not nomi:
                return JsonResponse({"success": False, "message": "Nomi kiritilishi kerak."}, status=400)

            is_active = data.get("is_active", "true").lower() == "true"  # Standart qiymat True
            kasb = Kasb.objects.create(nomi=nomi, is_active=is_active)
            return JsonResponse(
                {"success": True, "data": {"id": kasb.id, "nomi": kasb.nomi, "is_active": kasb.is_active}}
            )
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Noto'g'ri JSON ma'lumotlari."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)


class KasbUpdateView(View):
    """
    `Kasb` ob'yektini yangilashni amalga oshiruvchi View.
    """

    def patch(self, request, kasb_id, *args, **kwargs):
        """
        PATCH so'rovlar uchun `Kasb` ob'yektining `is_active` maydonini yangilaydi.
        """
        try:
            data = json.loads(request.body.decode('utf-8'))
            kasb = Kasb.objects.get(id=kasb_id)
            is_active = data.get("is_active", True)
            kasb.is_active = is_active
            kasb.save()
            return JsonResponse({"success": True, "message": "Faollik muvaffaqiyatli yangilandi."})
        except Kasb.DoesNotExist:
            return JsonResponse({"success": False, "message": "Kasb topilmadi."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Noto'g'ri JSON ma'lumotlari."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)


class YonalishListView(View):
    """
    `Yonalish` ob'yektlarini ro'yxatini olish va yangi yo'nalish qo'shishni amalga oshiruvchi View.
    """

    def get(self, request, *args, **kwargs):
        """
        GET so'rovlar uchun barcha `Yonalish` ob'yektlari ro'yxatini, shu jumladan bog'liq ma'lumotlarni qaytaradi.
        """
        yonalishlar = Yonalish.objects.select_related('kasb').prefetch_related('kurslar__groups').all().order_by('-created_at')
        data = [
            {
                "id": yonalish.id,
                "nomi": yonalish.nomi,
                "kasb_id": yonalish.kasb.id,
                "kasb_nomi": yonalish.kasb.nomi,
                "kurslar_soni": yonalish.kurslar.count(),
                "guruhlar_soni": sum(kurs.groups.count() for kurs in yonalish.kurslar.all())
            }
            for yonalish in yonalishlar
        ]
        return JsonResponse({"success": True, "data": data})

    def post(self, request, *args, **kwargs):
        """
        POST so'rovlar uchun yangi `Yonalish` ob'yektini yaratadi.
        """
        if request.content_type != "application/x-www-form-urlencoded":
            return JsonResponse({"success": False, "message": "Noto'g'ri kontent turi."}, status=400)

        try:
            nomi = request.POST.get("nomi")
            kasb_id = request.POST.get("kasb")
            if not nomi or not kasb_id:
                return JsonResponse({"success": False, "message": "Nomi va Kasb kiritilishi kerak."}, status=400)

            kasb = Kasb.objects.get(id=kasb_id)
            yonalish = Yonalish.objects.create(nomi=nomi, kasb=kasb)
            return JsonResponse(
                {"success": True, "data": {"id": yonalish.id, "nomi": yonalish.nomi, "kasb_nomi": kasb.nomi}}
            )
        except Kasb.DoesNotExist:
            return JsonResponse({"success": False, "message": "Noto'g'ri Kasb ID."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)


class KursListView(View):
    """
    `Kurs` ob'yektlarini ro'yxatini olish va yangi kurs qo'shishni amalga oshiruvchi View.
    """

    def get(self, request, *args, **kwargs):
        """
        GET so'rovlar uchun barcha `Kurs` ob'yektlari ro'yxatini qaytaradi.
        """
        kurslar = Kurs.objects.select_related('yonalish').prefetch_related('groups').all().order_by('-created_at')
        data = [
            {
                "id": kurs.id,
                "nomi": kurs.nomi,
                "narxi": kurs.narxi,
                "yonalish_id": kurs.yonalish.id,
                "yonalish_nomi": kurs.yonalish.nomi,
                "is_active": kurs.is_active,
                "guruh_count": kurs.groups.count(),
                "student_count": sum(group.students.count() for group in kurs.groups.all()),
                "created_at": kurs.created_at.strftime("%Y-%m-%d %H:%M"),
                "updated_at": kurs.updated_at.strftime("%Y-%m-%d %H:%M"),
            }
            for kurs in kurslar
        ]
        return JsonResponse({"success": True, "data": data})

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        """
        POST so'rovlar uchun yangi `Kurs` ob'yektini yaratadi.
        """
        if request.content_type != "application/x-www-form-urlencoded":
            return JsonResponse({"success": False, "message": "Noto'g'ri kontent turi."}, status=400)

        try:
            nomi = request.POST.get("nomi")
            narxi = request.POST.get("narxi")
            yonalish_id = request.POST.get("yonalish")
            if not nomi or not narxi or not yonalish_id:
                return JsonResponse({"success": False, "message": "Nomi, narxi va yo'nalish kiritilishi kerak."}, status=400)

            yonalish = Yonalish.objects.get(id=yonalish_id)
            kurs = Kurs.objects.create(nomi=nomi, narxi=narxi, yonalish=yonalish)
            return JsonResponse(
                {
                    "success": True,
                    "data": {
                        "id": kurs.id,
                        "nomi": kurs.nomi,
                        "narxi": kurs.narxi,
                        "yonalish_nomi": yonalish.nomi,
                    },
                }
            )
        except Yonalish.DoesNotExist:
            return JsonResponse({"success": False, "message": "Noto'g'ri Yo'nalish ID."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

