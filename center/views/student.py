import json

from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView, UpdateView
import base64
from account.models import CustomUser, Cashback, CashbackRecord
from center.models import Center, Filial, Images, SubmittedStudent, Kasb, Yonalish, Kurs, E_groups, StudentDetails, \
    GroupMembership
from school.models import Maktab, Sinf
from web_project import TemplateLayout



class StudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Filterlash uchun kerakli ma'lumotlar
        teachers = CustomUser.objects.filter(groups__name="Teacher")  # O'qituvchilar

        # Faqat SubmittedStudent bilan bog'langan yagona maktablar
        schools = Maktab.objects.filter(
            id__in=Sinf.objects.filter(
                submittedstudent__isnull=False
            ).values_list('maktab_id', flat=True)
        ).distinct()  # Yagona maktablar

        # Faqat SubmittedStudent bilan bog'langan yagona sinflar
        sinflar = Sinf.objects.filter(
            submittedstudent__isnull=False
        ).select_related('maktab', 'belgisi').distinct()  # Yagona sinflar

        # Boshqa ma'lumotlar
        kasblar = Kasb.objects.all()  # Kasblar
        yonalishlar = Yonalish.objects.all()  # Yo'nalishlar

        # SubmittedStudents ma'lumotlarini olish
        submitted_students = SubmittedStudent.objects.select_related(
            'filial', 'sinf', 'kasb', 'yonalish', 'added_by'
        ).prefetch_related('kurslar').order_by('-created_at')

        context.update({
            'teachers': teachers,  # O'qituvchilar ro'yxati
            'schools': schools,  # Faqat biriktirilgan maktablar (takrorlanmaydi)
            'sinflar': sinflar,  # Faqat biriktirilgan sinflar (takrorlanmaydi)
            'kasblar': kasblar,  # Kasblar ro'yxati
            'yonalishlar': yonalishlar,  # Yo'nalishlar ro'yxati
            'all_submitted_students': submitted_students,  # Talabalar ma'lumotlari
        })
        return context
    def post(self, request, *args, **kwargs):
        try:
            print("POST so'rovi qabul qilindi.")  # Debug
            student_id = request.POST.get('student_id')
            print(f"Talaba ID: {student_id}")  # Debug

            student = get_object_or_404(SubmittedStudent, id=student_id)
            print(f"Talaba topildi: {student}")  # Debug

            # Formadan kelgan ma'lumotlarni olish
            birth_date = request.POST.get('birth_date')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            parent_name = request.POST.get('parent_name')
            parent_phone = request.POST.get('parent_phone')
            photo_data = request.POST.get('photo_data')  # Kamera orqali yuborilgan rasm

            print(f"Olingan ma'lumotlar:\nTug'ilgan sana: {birth_date}\nJinsi: {gender}\n"
                  f"Manzil: {address}\nOta-onasi ismi: {parent_name}\n"
                  f"Telefon: {parent_phone}\nRasm mavjud: {bool(photo_data)}")  # Debug

            # Rasm mavjudligini tekshirish
            if not photo_data:
                print("Rasm topilmadi!")  # Debug
                return JsonResponse({
                    'success': False,
                    'message': "Iltimos, o'quvchining rasmini yuklang."
                })

            # Kamera orqali yuborilgan rasmni dekodlash
            print("Rasm dekodlanmoqda...")  # Debug
            format, imgstr = photo_data.split(';base64,')  # Base64 formatdan dekodlash
            ext = format.split('/')[-1]  # Fayl kengaytmasi olish
            photo_file = ContentFile(base64.b64decode(imgstr), name=f"{student_id}.{ext}")
            print(f"Rasm yaratildi: {photo_file}")  # Debug

            # Yaratilgan yoki mavjud StudentDetails obyektini yangilash
            print("StudentDetails yangilanmoqda yoki yaratilmoqda...")  # Debug
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
            print(f"StudentDetails yaratildi: {created}, Ma'lumotlar: {student_details}")  # Debug

            # Talabaning holatini "accepted" deb belgilash
            student.status = 'accepted'
            student.save()
            print("Talabaning holati 'accepted' deb belgilandi.")  # Debug

            # O'qituvchiga cashback biriktirish
            teacher = student.added_by
            if teacher and teacher.user_type == "2":  # Faqat o'qituvchilar uchun
                # Asosiy cashbackni topish
                cashback = Cashback.objects.filter(type="2", user_type="2", is_active=True).first()

                if not cashback:
                    print("Asosiy cashback topilmadi!")  # Debug
                    return JsonResponse({
                        'success': False,
                        'message': "Asosiy cashback topilmadi. Iltimos, admin bilan bog'laning."
                    }, status=400)

                # Individual cashback yozuvi yaratish
                cashback_record, created = CashbackRecord.objects.get_or_create(
                    cashback=cashback,
                    teacher=teacher,
                    student=student,
                )
                if created:
                    print(f"CashbackRecord yaratildi: {cashback_record}")  # Debug
                else:
                    print(f"CashbackRecord allaqachon mavjud: {cashback_record}")  # Debug

            return JsonResponse({
                'success': True,
                'message': 'Talaba maʼlumotlari muvaffaqiyatli saqlandi va holati qabul qilindi deb belgilandi.'
            })

        except Exception as e:
            print(f"Xatolik yuz berdi: {str(e)}")  # Debug
            return JsonResponse({
                'success': False,
                'message': f"Xatolik yuz berdi: {str(e)}"
            })

class AddGroupStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Accepted statusidagi o'quvchilarni olish
        accepted_students = SubmittedStudent.objects.filter(
            status='accepted'
        ).select_related(
            'filial', 'sinf__maktab', 'kasb', 'yonalish', 'added_by'
        ).prefetch_related(
            'kurslar', 'details'
        ).order_by('-created_at')

        # Filter uchun kerakli ma'lumotlarni olish
        teachers = CustomUser.objects.filter(groups__name="Teacher")  # O'qituvchilar

        # Faqat SubmittedStudent bilan bog'langan yagona maktablar
        schools = Maktab.objects.filter(
            id__in=Sinf.objects.filter(
                submittedstudent__isnull=False
            ).values_list('maktab_id', flat=True)
        ).distinct()

        # Sinflar: faqat biriktirilgan sinflar ro'yxati
        sinflar = Sinf.objects.filter(
            submittedstudent__isnull=False
        ).select_related('maktab', 'belgisi').distinct()

        # Boshqa ma'lumotlar
        kasblar = Kasb.objects.all()  # Kasblar
        yonalishlar = Yonalish.objects.all()  # Yo'nalishlar

        context.update({
            'teachers': teachers,  # O'qituvchilar ro'yxati
            'schools': schools,  # Faqat biriktirilgan maktablar (takrorlanmaydi)
            'sinflar': sinflar,  # Faqat biriktirilgan sinflar (takrorlanmaydi)
            'kasblar': kasblar,  # Kasblar ro'yxati
            'yonalishlar': yonalishlar,  # Yo'nalishlar ro'yxati
            'accepted_students': accepted_students,  # Faqat qabul qilingan o'quvchilar
        })
        return context

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        group_id = data.get('group_id')
        submitted_student_id = data.get('submitted_student_id')
        added_by_id = data.get('added_by_id')

        try:
            group = E_groups.objects.get(id=group_id)
            student = SubmittedStudent.objects.get(id=submitted_student_id)
            added_by = CustomUser.objects.get(id=added_by_id)

            # Tekshirish: O'quvchi ushbu guruhga allaqachon qo'shilganmi?
            if GroupMembership.objects.filter(group=group, student=student.added_by).exists():
                return JsonResponse({
                    "success": False,
                    "message": f"{student.first_name} {student.last_name} ushbu guruhga allaqachon qo'shilgan."
                }, status=400)

            # Guruhga o'quvchini qo'shish
            GroupMembership.objects.create(group=group, student=student.added_by)

            # SubmittedStudent statusini yangilash
            student.status = 'accept_group'
            student.save()

            return JsonResponse(
                {"success": True, "message": "O'quvchi guruhga muvaffaqiyatli qo'shildi va status yangilandi."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)


class PayStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Guruhga qabul qilingan o'quvchilarni olish
        students_in_groups = SubmittedStudent.objects.filter(
            status='accept_group'
        ).select_related(
            'filial', 'sinf__maktab', 'kasb', 'yonalish', 'added_by'
        ).prefetch_related(
            'kurslar', 'details', 'added_by__e_groups'  # O'quvchiga birikkan guruhlar uchun
        ).order_by('-created_at')

        # Filter uchun kerakli ma'lumotlarni olish
        teachers = CustomUser.objects.filter(groups__name="Teacher")  # O'qituvchilar

        # Faqat SubmittedStudent bilan bog'langan yagona maktablar
        schools = Maktab.objects.filter(
            id__in=Sinf.objects.filter(
                submittedstudent__isnull=False
            ).values_list('maktab_id', flat=True)
        ).distinct()

        # Sinflar: faqat biriktirilgan sinflar ro'yxati
        sinflar = Sinf.objects.filter(
            submittedstudent__isnull=False
        ).select_related('maktab', 'belgisi').distinct()

        # Boshqa ma'lumotlar
        kasblar = Kasb.objects.all()  # Kasblar
        yonalishlar = Yonalish.objects.all()  # Yo'nalishlar

        # Kontekstga qo'shish
        context.update({
            'teachers': teachers,  # O'qituvchilar ro'yxati
            'schools': schools,  # Maktablar ro'yxati
            'sinflar': sinflar,  # Sinflar ro'yxati
            'kasblar': kasblar,  # Kasblar ro'yxati
            'yonalishlar': yonalishlar,  # Yo'nalishlar ro'yxati
            'students_in_groups': students_in_groups,  # Guruhga qabul qilingan o'quvchilar
        })

        return context

class BlockStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context

class StatisticsStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context




def get_groups(request):
    groups = E_groups.objects.filter(is_active=True).select_related('kurs', 'center')

    # Ma'lumotlarni JSON formatida tayyorlash
    group_data = [
        {
            "id": group.id,
            "name": group.group_name,
            "course": group.kurs.nomi,
            "price": group.kurs.narxi,  # Kurs narxi qo'shildi
            "days": group.get_days_of_week_display(),
            "student_count": group.students.count(),
        }
        for group in groups
    ]

    return JsonResponse({"groups": group_data})