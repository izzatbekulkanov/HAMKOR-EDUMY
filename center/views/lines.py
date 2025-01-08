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

class LinesView(TemplateView):

    def get_context_data(self, **kwargs):
        """
        Sahifa uchun yo'nalishlar haqidagi ma'lumotlarni kontekstga qo'shish.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Foydalanuvchini olish
        user = self.request.user

        # Foydalanuvchiga biriktirilgan markazlar
        rahbar_center = Center.objects.filter(rahbari=user).first()
        filial_centers = Center.objects.filter(filial__admins=user).distinct()
        centers = set()
        if rahbar_center:
            centers.add(rahbar_center)
        centers.update(filial_centers)

        if not centers:
            context.update({
                'error': "Sizga biriktirilgan markaz mavjud emas.",
                'yonalishlar': [],
                'kasblar': [],  # Kasblar ro'yxati bo'sh
            })
            return context

        # Qidiruv parametri
        search_query = self.request.GET.get('q', '').strip()

        # Yo'nalishlarni olish
        if search_query:
            yonalishlar = Yonalish.objects.filter(
                center__in=centers,
                nomi__icontains=search_query
            )
        else:
            yonalishlar = Yonalish.objects.filter(center__in=centers)

        yonalishlar = yonalishlar.order_by('-created_at')

        # Kasblarni olish
        kasblar = Kasb.objects.filter(center__in=centers, is_active=True).order_by('nomi')

        # Ma'lumotlarni formatlash
        yonalishlar_data = []
        for yonalish in yonalishlar:
            kurs_count = yonalish.kurslar.count()
            guruh_count = sum(kurs.groups.count() for kurs in yonalish.kurslar.all())

            # Kasbni olish (agar mavjud bo'lsa)
            kasb_nomi = yonalish.kasb.nomi if yonalish.kasb else "Biriktirilmagan"

            yonalishlar_data.append({
                "id": yonalish.id,
                "nomi": yonalish.nomi,
                "created_at": yonalish.created_at,
                "updated_at": yonalish.updated_at,
                "is_active": yonalish.is_active,
                "kurs_count": kurs_count,
                "guruh_count": guruh_count,
                "kasb_nomi": kasb_nomi,  # Kasb nomini qo'shish
            })

        context.update({
            'yonalishlar': yonalishlar_data,
            'kasblar': kasblar,  # Kontekstga kasblarni qo'shish
            'search_query': search_query,
        })

        return context

    def post(self, request, *args, **kwargs):
        """
        POST so'rov: yangi yo'nalish qo'shadi.
        """
        # Foydalanuvchi kiritgan ma'lumotlarni olish
        nomi = request.POST.get("nomi", "").strip()
        kasb_id = request.POST.get("kasb", None)  # Kasb ID
        user_centers = Center.objects.filter(rahbari=request.user) | Center.objects.filter(filial__admins=request.user)

        # Foydalanuvchiga tegishli markazlarni olish
        if not nomi:
            return JsonResponse({"success": False, "message": "Yo'nalish nomi kiritilishi kerak."}, status=400)

        if not kasb_id:
            return JsonResponse({"success": False, "message": "Kasb tanlanishi kerak."}, status=400)

        if not user_centers.exists():
            return JsonResponse({"success": False, "message": "Sizga tegishli markaz topilmadi yoki ruxsat yo'q."},
                                status=403)

        try:
            # Markazni tanlash (faqat bitta markazni tanlang)
            center = user_centers.first()
            print(f"Tegishli markaz: {center}")

            # Kasbni tekshirish
            try:
                kasb = Kasb.objects.get(id=kasb_id, center=center)
            except Kasb.DoesNotExist:
                return JsonResponse({"success": False, "message": "Tanlangan kasb mavjud emas yoki ruxsat yo'q."},
                                    status=400)

            # Yo'nalish mavjudligini tekshirish
            if Yonalish.objects.filter(nomi__iexact=nomi, center=center, kasb=kasb).exists():
                return JsonResponse(
                    {"success": False, "message": f"'{nomi}' nomli yo'nalish ushbu kasb uchun allaqachon mavjud."},
                    status=400)

            # Yangi yo'nalish yaratish
            yonalish = Yonalish.objects.create(nomi=nomi, center=center, kasb=kasb, is_active=True)
            return JsonResponse({"success": True, "message": f"'{yonalish.nomi}' yo'nalishi muvaffaqiyatli qo'shildi."})

        except Exception as e:
            # Noma'lum xatoliklarni qaytarish
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    def delete(self, request, *args, **kwargs):
        """
        DELETE so'rov: yo'nalishni o'chiradi.
        """
        yonalish_id = kwargs.get('pk')

        try:
            yonalish = Yonalish.objects.get(id=yonalish_id)

            # Yo'nalishga kurslar birikkanligini tekshirish
            if yonalish.kurslar.exists():
                return JsonResponse(
                    {"success": False, "message": "Ushbu yo'nalishga kurslar birikkan, o'chirib bo'lmaydi."},
                    status=400
                )

            # Foydalanuvchining markazlariga tegishli ekanligini tekshirish
            user_centers = Center.objects.filter(rahbari=request.user) | Center.objects.filter(
                filial__admins=request.user
            )
            if yonalish.center not in user_centers:
                return JsonResponse(
                    {"success": False, "message": "Siz ushbu yo'nalishni o'chirishga ruxsatga ega emassiz."},
                    status=403
                )

            yonalish.delete()
            return JsonResponse({"success": True, "message": "Yo'nalish muvaffaqiyatli o'chirildi."})

        except Yonalish.DoesNotExist:
            return JsonResponse({"success": False, "message": "Yo'nalish topilmadi."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


class LinesDetailView(DetailView):
    model = Yonalish
    context_object_name = "yonalish"

    def get_object(self):
        """
        Returns the specific Yonalish object based on the primary key in the URL.
        """
        return get_object_or_404(Yonalish, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        """
        Prepares the context data for the template with detailed information about the Yonalish.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        yonalish = self.get_object()  # The specific Yonalish object

        # Fetch all related Kurs objects
        birikkan_kurslar = yonalish.kurslar.all()
        birikkan_kurslar_data = []
        for kurs in birikkan_kurslar:
            # Count active groups and students in the course
            groups = kurs.groups.all()
            group_count = groups.count()
            student_count = sum(group.students.count() for group in groups)

            birikkan_kurslar_data.append({
                "id": kurs.id,
                "nomi": kurs.nomi,
                "narxi": kurs.narxi,
                "group_count": group_count,
                "student_count": student_count,
                "created_at": kurs.created_at,
                "updated_at": kurs.updated_at,
            })

        # Fetch all unassociated Kurs objects
        all_kurslar = Kurs.objects.filter(center=yonalish.center)
        birikmagan_kurslar = all_kurslar.exclude(id__in=birikkan_kurslar.values_list('id', flat=True))
        birikmagan_kurslar_data = []
        for kurs in birikmagan_kurslar:
            birikmagan_kurslar_data.append({
                "id": kurs.id,
                "nomi": kurs.nomi,
                "narxi": kurs.narxi,
                "created_at": kurs.created_at,
                "updated_at": kurs.updated_at,
            })

        # Fetch all submitted students for the yonalish
        submitted_students = SubmittedStudent.objects.filter(yonalish=yonalish)
        submitted_students_data = []
        for student in submitted_students:
            submitted_students_data.append({
                "id": student.id,
                "full_name": f"{student.first_name} {student.last_name}",
                "phone_number": student.phone_number,
                "status": student.get_status_display(),
                "created_at": student.created_at,
                "updated_at": student.updated_at,
            })

        # Add data to the context
        context.update({
            "yonalish": yonalish,
            "birikkan_kurslar": birikkan_kurslar_data,
            "birikkan_kurslar_count": birikkan_kurslar.count(),
            "birikmagan_kurslar": birikmagan_kurslar_data,
            "birikmagan_kurslar_count": birikmagan_kurslar.count(),
            "submitted_students": submitted_students_data,
            "submitted_students_count": submitted_students.count(),
        })

        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles the addition or removal of a course from the Yonalish.
        Optimized for performance and security.
        """
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)

            # Validate and extract the course ID
            kurs_id = data.get("kurs_id")
            if not kurs_id:
                return JsonResponse({"success": False, "message": "Kurs ID yuborilishi kerak."}, status=400)

            # Fetch the related Yonalish object
            yonalish = self.get_object()

            # Validate the Kurs exists and belongs to the same center as the Yonalish
            kurs = get_object_or_404(Kurs, id=kurs_id, center=yonalish.center)

            # Check if the Kurs is already associated with the Yonalish
            if yonalish.kurslar.filter(id=kurs_id).exists():
                # Remove the Kurs from the Yonalish
                yonalish.kurslar.remove(kurs)
                return JsonResponse({"success": True, "message": f"'{kurs.nomi}' kursi yo'nalishdan olib tashlandi."})
            else:
                # Add the Kurs to the Yonalish
                yonalish.kurslar.add(kurs)
                return JsonResponse({"success": True, "message": f"'{kurs.nomi}' kursi yo'nalishga qo'shildi."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "JSON formatida noto'g'ri ma'lumot yuborildi."},
                                status=400)
        except Kurs.DoesNotExist:
            return JsonResponse({"success": False, "message": "Kurs topilmadi yoki ruxsat yo'q."}, status=404)
        except Exception as e:
            # Log exception (optional) and return a generic error
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)