import json
from collections import defaultdict

from django.utils.formats import number_format

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView, UpdateView
from django.db import transaction
from django.contrib.auth.decorators import login_required
from account.models import CustomUser
from center.models import Center, Filial, Images, SubmittedStudent, Kasb, Yonalish, Kurs, E_groups
from school.models import Sinf, Maktab, Belgisi
from web_project import TemplateLayout
from django.utils.decorators import method_decorator
from django.urls import reverse


class OccupationsView(TemplateView):

    def get_context_data(self, **kwargs):
        """
        Sahifa uchun ma'lumotlarni kontekstga qo'shish.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Foydalanuvchini olish
        user = self.request.user

        # Foydalanuvchiga biriktirilgan center (rahbari)
        rahbar_center = Center.objects.filter(rahbari=user).first()

        # Foydalanuvchi admin sifatida biriktirilgan filialga tegishli centerlarni olish
        filial_centers = Center.objects.filter(filial__admins=user).distinct()

        # Markazlarni birlashtirish (rahbar markaz + filial markazlari)
        centers = set()
        if rahbar_center:
            centers.add(rahbar_center)
        centers.update(filial_centers)

        if not centers:
            context.update({
                'error': "Sizga biriktirilgan markaz mavjud emas.",
                'kasblar': [],
            })
            return context

        # Qidiruv parametri
        search_query = self.request.GET.get('q', '').strip()

        # Kasblarni olish (barcha markazlarga tegishli)
        if search_query:
            kasblar = Kasb.objects.filter(center__in=centers, nomi__icontains=search_query)
        else:
            kasblar = Kasb.objects.filter(center__in=centers)

        kasblar = kasblar.order_by('-created_at')

        # Ma'lumotlarni formatlash
        kasblar_data = []
        for kasb in kasblar:
            yonalish_count = kasb.yonalishlar.count()
            kurs_count = sum(yonalish.kurslar.count() for yonalish in kasb.yonalishlar.all())
            guruh_count = sum(
                kurs.groups.count() for yonalish in kasb.yonalishlar.all() for kurs in yonalish.kurslar.all()
            )
            kasblar_data.append({
                "id": kasb.id,
                "nomi": kasb.nomi,
                "created_at": kasb.created_at,
                "updated_at": kasb.updated_at,
                "is_active": kasb.is_active,
                "yonalish_count": yonalish_count,
                "kurs_count": kurs_count,
                "guruh_count": guruh_count,
            })

        context.update({
            'kasblar': kasblar_data,
            'search_query': search_query,
        })

        return context

    def post(self, request, *args, **kwargs):
        """
        POST so'rov: Foydalanuvchiga biriktirilgan markazga yangi `Kasb` qo'shadi.
        """
        print(f"POST so'rov qabul qilindi. Foydalanuvchi: {request.user}")

        nomi = request.POST.get("nomi")
        if not nomi:
            print("Nomi kiritilmagan.")
            return HttpResponseRedirect(f"{request.path}?status=error&message=Kasb%20nomi%20kiritilishi%20kerak.")

        center = Center.objects.filter(rahbari=request.user).first()
        if not center:
            print("Foydalanuvchiga biriktirilmagan markazga urinish.")
            return HttpResponseRedirect(
                f"{request.path}?status=error&message=Sizga%20biriktirilgan%20markaz%20mavjud%20emas.")

        try:
            # Mavjud nomni tekshirish
            if Kasb.objects.filter(nomi__iexact=nomi, center=center).exists():
                print(f"'{nomi}' nomli kasb allaqachon mavjud.")
                return HttpResponseRedirect(
                    f"{request.path}?status=error&message='{nomi}'%20nomli%20kasb%20allaqachon%20mavjud.")

            # Yangi Kasb yaratish
            kasb = Kasb.objects.create(nomi=nomi, center=center, is_active=True)
            print(f"Yaratilgan Kasb: {kasb}")
            return HttpResponseRedirect(
                f"{request.path}?status=success&message='{kasb.nomi}'%20kasbi%20muvaffaqiyatli%20qo'shildi.")
        except Exception as e:
            print(f"POST so'rovda xato: {e}")
            return HttpResponseRedirect(f"{request.path}?status=error&message=Xatolik%20yuz%20berdi:%20{str(e)}")

    def delete(self, request, *args, **kwargs):
        """
        DELETE so'rov: Foydalanuvchiga biriktirilgan markazdagi `Kasb`ni o'chiradi.
        """
        kasb_id = kwargs.get('pk')  # URL orqali kelgan kasb ID

        try:
            kasb = Kasb.objects.get(id=kasb_id)

            # Kasbga yo'nalish birikkanligini tekshirish
            if kasb.yonalishlar.exists():
                return JsonResponse(
                    {"success": False, "message": "Ushbu kasbga yo'nalishlar birikkan, o'chirib bo'lmaydi."},
                    status=400)

            # Foydalanuvchining markazlariga tegishli ekanligini tekshirish
            user_centers = Center.objects.filter(rahbari=request.user) | Center.objects.filter(
                filial__admins=request.user)
            if kasb.center not in user_centers:
                return JsonResponse({"success": False, "message": "Siz ushbu kasbni o'chirishga ruxsatga ega emassiz."},
                                    status=403)

            kasb.delete()
            return JsonResponse({"success": True, "message": "Kasb muvaffaqiyatli o'chirildi."})

        except Kasb.DoesNotExist:
            return JsonResponse({"success": False, "message": "Kasb topilmadi."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


class OccupationsDetailView(DetailView):
    model = Kasb
    context_object_name = "kasb"

    def get_object(self):
        return get_object_or_404(Kasb, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        kasb = self.get_object()

        # Get all `Yonlishlar` associated with this `Kasb`
        yonalishlar = kasb.yonalishlar.all().order_by('-created_at')
        yonalishlar_data = []
        for yonalish in yonalishlar:
            kurslar = yonalish.kurslar.all()
            guruhlar_count = sum(kurs.groups.count() for kurs in kurslar)
            yonalishlar_data.append({
                "id": yonalish.id,
                "nomi": yonalish.nomi,
                "kurs_count": kurslar.count(),
                "guruh_count": guruhlar_count,
                "created_at": yonalish.created_at,
                "updated_at": yonalish.updated_at,
            })

        # Get all Yonalishlar that are not associated with this Kasb
        all_yonalishlar = Yonalish.objects.all()
        birikmagan_yonalishlar = all_yonalishlar.exclude(id__in=yonalishlar.values_list('id', flat=True))

        birikmagan_yonalishlar_data = []
        for yonalish in birikmagan_yonalishlar:
            # Kurslar va guruhlar sonini hisoblash
            kurslar = yonalish.kurslar.all()
            guruhlar_count = sum(kurs.groups.count() for kurs in kurslar)

            # Birikkan yoki birikmagan holatini aniqlash
            if yonalish.kasb:
                status = {
                    "type": "birikkan",
                    "kasb_nomi": yonalish.kasb.nomi,
                }
            else:
                status = {
                    "type": "birikmagan",
                    "kasb_nomi": None,
                }

            # Ma'lumotlarni yig'ish
            birikmagan_yonalishlar_data.append({
                "id": yonalish.id,
                "nomi": yonalish.nomi,
                "kurs_count": kurslar.count(),
                "guruh_count": guruhlar_count,
                "created_at": yonalish.created_at,
                "updated_at": yonalish.updated_at,
                "status": status,
            })

        context['yonalishlar'] = yonalishlar_data
        context['yonalishlar_count'] = len(yonalishlar_data)
        context['birikmagan_yonalishlar'] = birikmagan_yonalishlar_data
        context['birikmagan_yonalishlar_count'] = len(birikmagan_yonalishlar_data)
        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        kasb = get_object_or_404(Kasb, pk=kwargs['pk'])
        yonalish_id = request.POST.get('yonalish_id')

        try:
            yonalish = Yonalish.objects.get(pk=yonalish_id)

            # Tekshirish: Yo'nalish boshqa kasbga birikkanmi?
            if yonalish.kasb and yonalish.kasb != kasb:
                return JsonResponse({
                    "success": False,
                    "message": f"'{yonalish.nomi}' yo'nalishi boshqa kasbga birikkan."
                }, status=400)

            # Yo'nalishni olib tashlash yoki qo'shish
            if yonalish.kasb == kasb:
                # Yo'nalishni kasbdan olib tashlash
                yonalish.kasb = None
                yonalish.save()
                message = "Yo'nalish muvaffaqiyatli olib tashlandi."
            else:
                # Yo'nalishni kasbga qo'shish
                yonalish.kasb = kasb
                yonalish.save()
                message = "Yo'nalish muvaffaqiyatli qo'shildi."

            return JsonResponse({"success": True, "message": message})

        except Yonalish.DoesNotExist:
            return JsonResponse({"success": False, "message": "Yo'nalish topilmadi."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

