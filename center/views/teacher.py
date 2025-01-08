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


class TeacherView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # SubmittedStudents ma'lumotlarini olish
        submitted_students = SubmittedStudent.objects.select_related(
            'filial', 'sinf', 'kasb', 'yonalish'
        ).prefetch_related('kurslar').order_by('-created_at')

        context.update({
            'grades': range(1, 12),  # 1-dan 11-gacha sinflar
            'submitted_students': submitted_students,  # Talabalar ma'lumotlari
        })
        return context
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            print("POST so'rov qabul qilindi.")  # Debug

            if not request.body:
                print("So'rov bo'sh.")  # Debug
                return JsonResponse({"success": False, "message": "JSON ma'lumotlari bo'sh."}, status=400)

            try:
                data = json.loads(request.body)
                print(f"Olingan JSON ma'lumotlari: {data}")  # Debug
            except json.JSONDecodeError as e:
                print(f"JSON xatosi: {e}")  # Debug
                return JsonResponse({"success": False, "message": "Noto'g'ri JSON formati."}, status=400)

            # Ma'lumotlarni olish
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            phone_number = data.get('phone_number', '').strip()
            sinf_raqami = data.get('sinf')  # Sinf raqami
            kasb_id = data.get('kasb')
            yonalish_id = data.get('yonalish')
            kurs_ids = data.get('kurslar', [])
            filial_id = data.get('filial')
            belgisi_name = data.get('belgisi', '').strip()  # Belgisi nomi
            school_id = data.get('school')

            print(f"Qabul qilingan ma'lumotlar: first_name={first_name}, last_name={last_name}, "
                  f"phone_number={phone_number}, sinf_raqami={sinf_raqami}, kasb_id={kasb_id}, "
                  f"yonalish_id={yonalish_id}, kurslar={kurs_ids}, filial_id={filial_id}, belgisi={belgisi_name}, school_id={school_id}")  # Debug

            if not all([first_name, last_name, phone_number, sinf_raqami, kasb_id, yonalish_id, filial_id, school_id,
                        belgisi_name]):
                print("Majburiy maydonlar kiritilmagan.")  # Debug
                return JsonResponse({"success": False, "message": "Majburiy maydonlar kiritilishi kerak."}, status=400)

            # Ob'ektlarni olish
            kasb = Kasb.objects.filter(id=kasb_id).first()
            yonalish = Yonalish.objects.filter(id=yonalish_id).first()
            filial = Filial.objects.filter(id=filial_id).first()
            kurslar = Kurs.objects.filter(id__in=kurs_ids)
            school = Maktab.objects.filter(id=school_id).first()

            if not all([kasb, yonalish, filial, school]):
                print("Bir yoki bir nechta ob'ekt topilmadi.")  # Debug
                return JsonResponse({"success": False, "message": "Bir yoki bir nechta ob'ekt topilmadi."}, status=404)

            # Belgisini olish yoki yaratish
            belgisi = Belgisi.objects.filter(nomi=belgisi_name).first()
            if not belgisi:
                belgisi = Belgisi.objects.create(nomi=belgisi_name)
                print(f"Belgisi yaratildi: {belgisi}")  # Debug

            # Sinfni olish yoki yaratish
            sinf = Sinf.objects.filter(sinf_raqami=sinf_raqami, maktab=school, belgisi=belgisi, is_active=True).first()
            if not sinf:
                sinf = Sinf.objects.create(sinf_raqami=sinf_raqami, maktab=school, belgisi=belgisi, is_active=True)
                print(f"Sinf yaratildi: {sinf}")  # Debug

            print(
                f"Fetched objects: kasb={kasb}, yonalish={yonalish}, filial={filial}, school={school}, belgisi={belgisi}, sinf={sinf}")  # Debug

            # Talaba yaratish
            submitted_student = SubmittedStudent.objects.create(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                sinf=sinf,
                kasb=kasb,
                yonalish=yonalish,
                filial=filial,
                belgisi=belgisi_name,
                added_by=request.user
            )
            print(f"Yaratilgan talaba: {submitted_student}")  # Debug

            # Kurslarni bog‘lash
            submitted_student.kurslar.set(kurslar)
            print(f"Talabaga kurslar bog'landi: {kurslar}")  # Debug

            return JsonResponse({"success": True, "message": "Talaba muvaffaqiyatli qo‘shildi."}, status=201)

        except Exception as e:
            print(f"Noma'lum xatolik: {e}")  # Debug
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)