from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView, UpdateView
import base64
from account.models import CustomUser
from center.models import Center, Filial, Images, SubmittedStudent, Kasb, Yonalish, Kurs, E_groups, StudentDetails
from school.models import Maktab, Sinf
from web_project import TemplateLayout



class StudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Filterlash uchun kerakli ma'lumotlar
        teachers = CustomUser.objects.filter(groups__name="Teacher")
        schools = Maktab.objects.all()
        sinflar = Sinf.objects.select_related('maktab', 'belgisi')
        kasblar = Kasb.objects.all()
        yonalishlar = Yonalish.objects.all()

        # SubmittedStudents ma'lumotlarini olish
        submitted_students = SubmittedStudent.objects.select_related(
            'filial', 'sinf', 'kasb', 'yonalish', 'added_by'
        ).prefetch_related('kurslar').order_by('-created_at')

        context.update({
            'teachers': teachers,  # O'qituvchilar ro'yxati
            'schools': schools,    # Maktablar ro'yxati
            'sinflar': sinflar,    # Sinflar ro'yxati
            'kasblar': kasblar,    # Kasblar ro'yxati
            'yonalishlar': yonalishlar,  # Yo'nalishlar ro'yxati
            'all_submitted_students': submitted_students,  # Talabalar ma'lumotlari
        })
        return context

    def post(self, request, *args, **kwargs):
        try:
            student_id = request.POST.get('student_id')
            student = get_object_or_404(SubmittedStudent, id=student_id)

            # Formadan kelgan ma'lumotlarni olish
            birth_date = request.POST.get('birth_date')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            parent_name = request.POST.get('parent_name')
            parent_phone = request.POST.get('parent_phone')
            photo_data = request.POST.get('photo_data')  # Kamera orqali yuborilgan rasm

            # Agar kamera orqali yuborilgan rasm mavjud bo'lsa
            photo_file = None
            if photo_data:
                format, imgstr = photo_data.split(';base64,')  # Base64 formatdan dekodlash
                ext = format.split('/')[-1]  # Fayl kengaytmasi olish
                photo_file = ContentFile(base64.b64decode(imgstr), name=f"{student_id}.{ext}")

            # Yaratilgan yoki mavjud StudentDetails obyektini yangilash
            student_details, created = StudentDetails.objects.update_or_create(
                student=student,
                defaults={
                    'birth_date': birth_date,
                    'gender': gender,
                    'address': address,
                    'parent_name': parent_name,
                    'parent_phone': parent_phone,
                    'photo': photo_file,
                }
            )

            # Talabaning holatini "accepted" deb belgilash
            student.status = 'accepted'
            student.save()

            return JsonResponse({
                'success': True,
                'message': 'Talaba maʼlumotlari muvaffaqiyatli saqlandi va holati qabul qilindi deb belgilandi.'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"Xatolik yuz berdi: {str(e)}"
            })

class AddGroupStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

class PayStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

class BlockStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

class StatisticsStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context