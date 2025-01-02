from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from center.models import Kasb, Yonalish, Kurs, Center
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json


@method_decorator([csrf_exempt, login_required], name='dispatch')
class KasbListView(View):
    """
    Foydalanuvchiga biriktirilgan markazlar bo‘yicha `Kasb` ob'yektlarini boshqaruvchi View.
    """

    def get(self, request, *args, **kwargs):
        """
        GET so'rov: Foydalanuvchiga biriktirilgan markazlar va filiallar orqali `Kasb` ob'yektlarini qaytaradi.
        """
        print(f"GET so'rov qabul qilindi. Foydalanuvchi: {request.user}")  # Debugging

        # Foydalanuvchiga biriktirilgan center (rahbari)
        rahbar_center = Center.objects.filter(rahbari=request.user).first()

        # Foydalanuvchi admin sifatida biriktirilgan filialga tegishli centerlarni olish
        filial_centers = Center.objects.filter(filial__admins=request.user).distinct()

        # Markazlarni birlashtirish (rahbar markaz + filial markazlari)
        centers = set()
        if rahbar_center:
            centers.add(rahbar_center)
        centers.update(filial_centers)

        if not centers:
            print("Foydalanuvchiga hech qanday markaz biriktirilmagan.")  # Debugging
            return JsonResponse({"success": False, "message": "Sizga biriktirilgan markaz mavjud emas."}, status=403)

        print(f"Foydalanuvchiga biriktirilgan markazlar: {centers}")  # Debugging

        # Kasblarni filtr qilish (barcha markazlarga tegishli)
        kasblar = Kasb.objects.filter(center__in=centers).order_by('-created_at')
        print(f"Kasblar soni: {kasblar.count()}")  # Debugging

        # Ma'lumotlarni formatlash
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

        print(f"Qaytarilayotgan ma'lumot: {data}")  # Debugging
        return JsonResponse({"success": True, "data": data})

    def post(self, request, *args, **kwargs):
        """
        POST so'rov: Foydalanuvchiga biriktirilgan markazga yangi `Kasb` qo'shadi.
        """
        print(f"POST so'rov qabul qilindi. Foydalanuvchi: {request.user}")  # Debugging

        if request.content_type != "application/json":
            print("Noto'g'ri kontent turi qabul qilindi.")  # Debugging
            return JsonResponse(
                {"success": False, "message": "Noto'g'ri kontent turi. `application/json` bo'lishi kerak."},
                status=400
            )

        try:
            data = json.loads(request.body.decode('utf-8'))  # So'rov tanasini dekodlash
            print(f"Qabul qilingan JSON ma'lumotlari: {data}")  # Debugging

            nomi = data.get("nomi")
            if not nomi:
                print("Nomi kiritilmagan.")  # Debugging
                return JsonResponse({"success": False, "message": "Nomi kiritilishi kerak."}, status=400)

            # Foydalanuvchiga biriktirilgan markazni olish
            center = Center.objects.filter(rahbari=request.user).first()
            if not center:
                print("Foydalanuvchiga biriktirilmagan markazga urinish.")  # Debugging
                return JsonResponse({"success": False, "message": "Sizga biriktirilgan markaz mavjud emas."}, status=403)

            # Yangi Kasb yaratish
            is_active = data.get("is_active", "true").lower() == "true"  # Standart qiymat True
            print(f"Yaratilayotgan Kasb: nomi={nomi}, center={center}, is_active={is_active}")  # Debugging

            kasb = Kasb.objects.create(nomi=nomi, center=center, is_active=is_active)
            print(f"Yaratilgan Kasb: {kasb}")  # Debugging

            return JsonResponse(
                {"success": True, "data": {"id": kasb.id, "nomi": kasb.nomi, "center": kasb.center.nomi, "is_active": kasb.is_active}}
            )
        except json.JSONDecodeError as e:
            print(f"JSON ma'lumotlarida xato: {e}")  # Debugging
            return JsonResponse({"success": False, "message": "Noto'g'ri JSON ma'lumotlari."}, status=400)
        except Exception as e:
            print(f"POST so'rovda xato: {e}")  # Debugging
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
        print("GET so'rov qabul qilindi.")  # Debugging

        yonalishlar = Yonalish.objects.select_related('kasb').prefetch_related('kurslar__groups').all().order_by('-created_at')
        print(f"Yonalishlar soni: {yonalishlar.count()}")  # Debugging

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

        print(f"Qaytarilayotgan ma'lumot: {data}")  # Debugging
        return JsonResponse({"success": True, "data": data})

    def post(self, request, *args, **kwargs):
        """
        POST so'rovlar uchun yangi `Yonalish` ob'yektini yaratadi.
        """
        print("POST so'rov qabul qilindi.")  # Debugging

        if request.content_type != "application/x-www-form-urlencoded":
            print("Noto'g'ri kontent turi qabul qilindi.")  # Debugging
            return JsonResponse({"success": False, "message": "Noto'g'ri kontent turi."}, status=400)

        try:
            nomi = request.POST.get("nomi")
            kasb_id = request.POST.get("kasb")
            print(f"Kiritilgan nomi: {nomi}, kasb_id: {kasb_id}")  # Debugging

            if not nomi or not kasb_id:
                print("Nomi yoki Kasb ID kiritilmagan.")  # Debugging
                return JsonResponse({"success": False, "message": "Nomi va Kasb kiritilishi kerak."}, status=400)

            kasb = Kasb.objects.get(id=kasb_id)
            print(f"Topilgan Kasb: ID={kasb.id}, nomi={kasb.nomi}")  # Debugging

            # Foydalanuvchiga biriktirilgan markazni olish
            center = Center.objects.filter(rahbari=request.user).first()
            if not center:
                print("Foydalanuvchiga biriktirilmagan markazga urinish.")  # Debugging
                return JsonResponse({"success": False, "message": "Sizga biriktirilgan markaz mavjud emas."},
                                    status=403)

            yonalish = Yonalish.objects.create(nomi=nomi, kasb=kasb, center=center)
            print(f"Yaratilgan Yonalish: ID={yonalish.id}, nomi={yonalish.nomi}, center={center.nomi}")  # Debugging



            return JsonResponse(
                {"success": True, "data": {"id": yonalish.id, "nomi": yonalish.nomi, "kasb_nomi": kasb.nomi}}
            )
        except Kasb.DoesNotExist:
            print(f"Noto'g'ri Kasb ID: {kasb_id}")  # Debugging
            return JsonResponse({"success": False, "message": "Noto'g'ri Kasb ID."}, status=400)
        except Exception as e:
            print(f"POST so'rovda xato: {e}")  # Debugging
            return JsonResponse({"success": False, "message": str(e)}, status=400)

class YonalishUpdateView(View):
    """
    `Yonalish` ob'yektini yangilashni amalga oshiruvchi View.
    """

    def patch(self, request, yonalish_id, *args, **kwargs):
        """
        PATCH so'rovlar uchun `Yonalish` ob'yektining `is_active` maydonini yangilaydi.
        """
        try:
            data = json.loads(request.body.decode('utf-8'))
            yonalish = Yonalish.objects.get(id=yonalish_id)
            is_active = data.get("is_active", True)
            yonalish.is_active = is_active
            yonalish.save()
            return JsonResponse({"success": True, "message": "Faollik muvaffaqiyatli yangilandi."})
        except Yonalish.DoesNotExist:
            return JsonResponse({"success": False, "message": "Yonalish topilmadi."}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Noto'g'ri JSON ma'lumotlari."}, status=400)
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
            print("[DEBUG] Noto'g'ri kontent turi:", request.content_type)
            return JsonResponse({"success": False, "message": "Noto'g'ri kontent turi."}, status=400)

        try:
            nomi = request.POST.get("nomi")
            narxi = request.POST.get("narxi")

            print(f"[DEBUG] POST ma'lumotlar: nomi={nomi}, narxi={narxi}")

            if not nomi or not narxi:
                print("[DEBUG] Kerakli ma'lumotlar yo'q:", {
                    "nomi": nomi, "narxi": narxi
                })
                return JsonResponse({"success": False, "message": "Nomi, narxi va yo'nalish kiritilishi kerak."},
                                    status=400)

            # Foydalanuvchiga biriktirilgan markazni olish
            center = Center.objects.filter(rahbari=request.user).first()
            print(f"[DEBUG] Foydalanuvchiga biriktirilgan markaz: {center}")

            if not center:
                print("[DEBUG] Foydalanuvchiga biriktirilmagan markazga urinish.")
                return JsonResponse({"success": False, "message": "Sizga biriktirilgan markaz mavjud emas."},
                                    status=403)

            kurs = Kurs.objects.create(nomi=nomi, narxi=narxi, center=center)
            print(f"[DEBUG] Yaratilgan Kurs: {kurs}")

            return JsonResponse(
                {
                    "success": True,
                    "data": {
                        "id": kurs.id,
                        "nomi": kurs.nomi,
                        "narxi": kurs.narxi,
                    },
                }
            )
        except Exception as e:
            print(f"[DEBUG] Xato yuz berdi: {e}")
            return JsonResponse({"success": False, "message": str(e)}, status=400)

class GetKasbAndYonalishView(View):
    """
    Kasb, Yo'nalish va Kurslarni olish uchun API.
    """

    def get(self, request, *args, **kwargs):
        try:
            # Barcha faol kasblarni olish
            kasb_list = Kasb.objects.filter(is_active=True)

            # Kasb ma'lumotlarini tayyorlash
            kasb_data = []
            for kasb in kasb_list:
                # Ushbu kasbga tegishli faol yo'nalishlarni olish
                yonalish_data = []
                yonalish_list = Yonalish.objects.filter(kasb=kasb, is_active=True)

                for yonalish in yonalish_list:
                    # Yo'nalishga tegishli faol kurslarni olish
                    kurs_data = Kurs.objects.filter(yonalishlar=yonalish, is_active=True).values(
                        'id', 'nomi', 'narxi'
                    )

                    yonalish_data.append({
                        "id": yonalish.id,
                        "name": yonalish.nomi,
                        "kurslar": list(kurs_data),
                    })

                kasb_data.append({
                    "id": kasb.id,
                    "name": kasb.nomi,
                    "yonalishlar": yonalish_data
                })

            return JsonResponse({
                "success": True,
                "kasb": kasb_data
            }, status=200)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class KursUpdateView(View):
    """
    View to handle course status updates.
    """

    def patch(self, request, yonalish_id, *args, **kwargs):
        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)
            is_active = data.get('is_active')
            kurs_id = data.get('kurs_id')

            if kurs_id is None or is_active is None:
                return JsonResponse({"success": False, "message": "Kurs ID va holat talab qilinadi."}, status=400)

            # Get the course object and check permissions
            kurs = get_object_or_404(
                Kurs,
                id=kurs_id,
                center__in=Center.objects.filter(rahbari=request.user) | Center.objects.filter(filial__admins=request.user)
            )

            # Update the active status
            kurs.is_active = is_active
            kurs.save()

            message = "Kurs faollik holati muvaffaqiyatli yangilandi." if is_active else "Kurs faollik holati o'chirildi."
            return JsonResponse({"success": True, "message": message})

        except Kurs.DoesNotExist:
            return JsonResponse({"success": False, "message": "Kurs topilmadi."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)