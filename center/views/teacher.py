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
from account.models import CustomUser, CashbackRecord
from center.models import Center, Filial, Images, SubmittedStudent, Kasb, Yonalish, Kurs, E_groups
from school.models import Sinf, Maktab, Belgisi
from web_project import TemplateLayout
from django.utils.decorators import method_decorator
from django.urls import reverse



class TeacherCashbackView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        teacher = self.request.user

        # Faqat o'qituvchilar uchun cashback yozuvlarini olish
        if teacher.user_type != "2":
            context['error'] = "Sizda cashback yozuvlari yo'q."
            return context

        # Cashback yozuvlarini olish
        cashback_records = CashbackRecord.objects.filter(teacher=teacher).select_related(
            'cashback', 'student', 'student__sinf', 'student__sinf__maktab'
        )

        # Summalarni hisoblash
        total_cashback = 0
        paid_cashback = 0
        unpaid_cashback = 0
        total_from_students = 0
        student_count = 0

        cashback_data = []
        for record in cashback_records:
            maktab = record.student.sinf.maktab if record.student.sinf and record.student.sinf.maktab else None
            cashback_amount = record.cashback.summasi

            # Umumiy summalarni yangilash
            total_cashback += cashback_amount
            if record.is_paid:
                paid_cashback += cashback_amount
            else:
                unpaid_cashback += cashback_amount
                total_from_students += cashback_amount
                student_count += 1

            cashback_data.append({
                "maktab_raqami": maktab.maktab_raqami if maktab else "Noma'lum",
                "maktab_nomi": maktab.nomi if maktab else "Noma'lum",
                "student": {
                    "class_number": record.student.sinf.sinf_raqami if record.student.sinf else "Noma'lum",
                    "belgisi": record.student.belgisi,
                    "first_name": record.student.first_name,
                    "last_name": record.student.last_name,
                    "phone_number": record.student.phone_number,
                },
                "cashback_amount": cashback_amount,
                "is_paid": record.is_paid,
                "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "student_status": record.student.get_status_display(),
                "status_color": self.get_status_color(record.student.status),
            })

        # Konteksga summalarni qo‘shish
        context['cashback_data'] = cashback_data
        context['total_cashback'] = total_cashback
        context['paid_cashback'] = paid_cashback
        context['unpaid_cashback'] = unpaid_cashback
        context['total_from_students'] = total_from_students
        context['student_count'] = student_count

        return context

    @staticmethod
    def get_status_color(status):
        """
        Qabul holati uchun mos rangni qaytaradi.
        """
        color_map = {
            'pending': 'warning',
            'accepted': 'success',
            'accept_group': 'primary',
            'rejected': 'danger',
        }
        return color_map.get(status, 'secondary')  # Default rang: secondary


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