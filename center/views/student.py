import json
import traceback
from datetime import timedelta, date, datetime
from decimal import Decimal

from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Sum, Count, Q, F, CharField
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce, Concat
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView, UpdateView
import base64
from account.models import CustomUser, Cashback, CashbackRecord
from center.models import Center, Filial, Images, SubmittedStudent, Kasb, Yonalish, Kurs, E_groups, StudentDetails, \
    GroupMembership, PaymentRecord
from school.models import Maktab, Sinf
from web_project import TemplateLayout
from django.utils.timezone import now


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
            print("📩 [DEBUG] POST so'rovi qabul qilindi.")  # Debug log

            student_id = request.POST.get('student_id')
            if not student_id:
                return JsonResponse({'success': False, 'message': "Talaba ID topilmadi!"}, status=400)

            student = get_object_or_404(SubmittedStudent, id=student_id)
            print(f"✅ [DEBUG] Talaba topildi: {student}")  # Debug

            # Formadan kelgan ma'lumotlarni olish
            birth_date = request.POST.get('birth_date')
            gender = request.POST.get('gender')
            address = request.POST.get('address')
            parent_name = request.POST.get('parent_name')
            parent_phone = request.POST.get('parent_phone')
            photo_data = request.POST.get('photo_data')

            # Tug‘ilgan sanani formatga moslashtirish
            try:
                if birth_date:
                    birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'success': False, 'message': "Tug'ilgan sana noto‘g‘ri formatda!"}, status=400)

            print(
                f"📋 [DEBUG] Ma'lumotlar: Jinsi={gender}, Manzil={address}, Ota-ona={parent_name}, Tel={parent_phone}, Rasm bor={bool(photo_data)}")  # Debug

            # **📌 Rasmni dekodlash**
            photo_file = None
            if photo_data:
                try:
                    print("🖼️ [DEBUG] Rasm dekodlanmoqda...")  # Debug
                    format, imgstr = photo_data.split(';base64,')
                    ext = format.split('/')[-1]
                    photo_file = ContentFile(base64.b64decode(imgstr), name=f"{student_id}.{ext}")
                except Exception as e:
                    print(f"❌ [DEBUG] Rasm dekodlashda xatolik: {str(e)}")  # Debug
                    return JsonResponse({'success': False, 'message': "Rasmni qayta yuklang!"}, status=400)

            # **📌 Talabaning ma'lumotlarini saqlash**
            with transaction.atomic():
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
                print(f"✅ [DEBUG] StudentDetails yangilandi: {student_details}")  # Debug

                # **📌 Talabaning holatini yangilash**
                student.status = 'accepted'
                student.save()
                print("✅ [DEBUG] Talabaning holati 'accepted' deb belgilandi.")  # Debug

                # **📌 O'qituvchiga cashback tayinlash**
                teacher = student.added_by
                if teacher and getattr(teacher, 'user_type', None) == "2":  # O'qituvchi ekanligini tekshirish
                    cashback = Cashback.objects.filter(type="2", user_type="2", is_active=True).first()

                    if cashback:
                        cashback_record, created = CashbackRecord.objects.get_or_create(
                            cashback=cashback,
                            teacher=teacher,
                            student=student,
                        )
                        print(f"✅ [DEBUG] CashbackRecord yaratildi: {cashback_record}")  # Debug
                    else:
                        print("⚠️ [DEBUG] Cashback topilmadi, lekin jarayon davom etmoqda.")  # Debug

            return JsonResponse({
                'success': True,
                'message': "Talaba maʼlumotlari muvaffaqiyatli saqlandi va qabul qilindi!"
            })

        except Exception as e:
            print(f"❌ [DEBUG] Xatolik yuz berdi: {str(e)}")  # Debug
            return JsonResponse({'success': False, 'message': f"Xatolik yuz berdi: {str(e)}"}, status=500)


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
        print("\n🟢 [DEBUG] POST so‘rovi qabul qilindi. O‘quvchini guruhga qo‘shish boshlanmoqda...")

        try:
            data = json.loads(request.body)
            group_id = data.get('group_id')
            submitted_student_id = data.get('submitted_student_id')

            print(
                f"📩 [DEBUG] So‘rovdan olingan ma’lumotlar: group_id={group_id}, submitted_student_id={submitted_student_id}")

            # ✅ **Guruh va o‘quvchini olish**
            try:
                group = E_groups.objects.get(id=group_id)
                student = SubmittedStudent.objects.get(id=submitted_student_id)
            except E_groups.DoesNotExist:
                return JsonResponse({"success": False, "message": "Guruh topilmadi!"}, status=400)
            except SubmittedStudent.DoesNotExist:
                return JsonResponse({"success": False, "message": "O‘quvchi topilmadi!"}, status=400)

            print(f"✅ [DEBUG] Guruh topildi: {group.group_name} | Kurs: {group.kurs.nomi}")
            print(f"✅ [DEBUG] O‘quvchi topildi: {student.first_name} {student.last_name}")

            # ✅ **Tekshirish: O‘quvchi allaqachon ushbu guruhda bormi?**
            if GroupMembership.objects.filter(group=group, student=student).exists():
                return JsonResponse({"success": False,
                                     "message": f"{student.first_name} {student.last_name} ushbu guruhga allaqachon qo‘shilgan."},
                                    status=400)

            # ✅ **Dars kunlari tekshiruvi**
            all_days = group.days_of_week
            if not all_days:
                return JsonResponse(
                    {"success": False, "message": f"{group.group_name} guruhida dars kunlari belgilanmagan!"},
                    status=400)

            # ✅ **Qarzdorlik hisoblash**
            today = now().date()
            payment_data = PaymentRecord.calculate_payment(student, group, today)

            # 🔴 **Agar joriy oyda dars kunlari bo‘lmasa, keyingi oyni hisoblash**
            if payment_data['total_lessons_in_month'] == 0:
                print("⚠️ [DEBUG] Joriy oyda dars kunlari mavjud emas. Keyingi oyga qarzdorlik o'tkaziladi.")

                # **Keyingi oyga o'tkazish**
                next_month = (today.month % 12) + 1
                next_year = today.year + (1 if next_month == 1 else 0)
                payment_data = PaymentRecord.calculate_payment(student, group, date(next_year, next_month, 1))

                payment_month = next_month
                payment_year = next_year
            else:
                payment_month = today.month
                payment_year = today.year

            # ✅ **Agar barcha tekshiruvlardan muvaffaqiyatli o‘tsa, tranzaksiya boshlanadi**
            with transaction.atomic():
                GroupMembership.objects.create(group=group, student=student)
                student.status = 'accept_group'
                student.save()

                PaymentRecord.objects.create(
                    student=student,
                    group=group,
                    month=payment_month,
                    year=payment_year,
                    amount_paid=0,
                    total_debt=payment_data['total_debt'],
                    remaining_balance=payment_data['remaining_balance'],
                    payment_date=today,
                    total_lessons_in_month=payment_data['total_lessons_in_month'],
                    attended_lessons=payment_data['attended_lessons'],
                    course_total_price=group.kurs.narxi,
                )

                return JsonResponse({
                    "success": True,
                    "message": f"{student.first_name} {student.last_name} guruhga muvaffaqiyatli qo‘shildi va qarzdorlik yaratildi.",
                    **payment_data,
                    "payment_date": str(today),
                    "course_total_price": f"{group.kurs.narxi:.2f}",
                    "payment_month": payment_month,
                    "payment_year": payment_year
                })

        except Exception as e:
            print(f"❌ [DEBUG] Xatolik yuz berdi: {str(e)}")
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=400)


class PayStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # 🔹 **Hozirgi yil va oyni olish**
        current_year = now().year
        current_month = now().month

        # 🔹 **Bazadagi mavjud yillar**
        years = PaymentRecord.objects.values_list('year', flat=True).distinct().order_by('-year')

        # 🔹 **Tanlangan yil va oy**
        selected_year = int(self.request.GET.get('year', current_year))
        selected_month = int(self.request.GET.get('month', current_month))
        selected_group_id = self.request.GET.get('group_id')

        # 🔹 **Tanlangan yil bo‘yicha mavjud oylar**
        months = PaymentRecord.objects.filter(year=selected_year).values_list('month', flat=True).distinct().order_by(
            'month')

        # 🔹 **Har bir oyda nechta qarzdor borligini hisoblash**
        month_debt_counts = PaymentRecord.objects.filter(year=selected_year).values('month').annotate(
            debtors=Count('id', filter=~Q(remaining_balance=0))
        ).order_by('month')
        month_debt_counts = {item['month']: item['debtors'] for item in month_debt_counts}

        # 🔹 **Tanlangan yil+oy bo‘yicha mavjud guruhlar**
        groups = E_groups.objects.filter(
            id__in=PaymentRecord.objects.filter(year=selected_year, month=selected_month).values_list('group',
                                                                                                      flat=True)
        ).select_related('kurs')

        group_data = []
        selected_group = None

        if selected_group_id:
            selected_group = get_object_or_404(E_groups, id=selected_group_id)

            # 🔹 **Ushbu guruhga tegishli o‘quvchilarni olish**
            students = selected_group.students.filter(Q(status='accept_group') | Q(status='paid'))

            student_list = []
            total_group_paid = 0  # Guruh bo‘yicha jami to‘langan summa
            total_group_debt = 0  # Guruh bo‘yicha jami qarzdorlik

            for student in students:
                payment_info = PaymentRecord.objects.filter(
                    student=student, group=selected_group, month=selected_month, year=selected_year
                ).aggregate(
                    total_paid=Coalesce(Sum('amount_paid', output_field=DecimalField()),
                                        Value(0, output_field=DecimalField())),
                    total_debt=Coalesce(Sum('total_debt', output_field=DecimalField()),
                                        Value(0, output_field=DecimalField())),
                    remaining_balance=Coalesce(Sum('remaining_balance', output_field=DecimalField()),
                                               Value(0, output_field=DecimalField())),
                )

                student_list.append({
                    'id': student.id,
                    'status': student.status,
                    'full_name': f"{student.first_name} {student.last_name}",
                    'total_paid': round(payment_info['total_paid']),
                    'total_debt': round(payment_info['total_debt']),
                    'remaining_balance': round(payment_info['remaining_balance']),
                })

                total_group_paid += payment_info['total_paid']
                total_group_debt += payment_info['total_debt']

            group_data.append({
                'group_id': selected_group.id,
                'group_name': selected_group.group_name,
                'kurs_narxi': selected_group.kurs.narxi,
                'total_group_paid': total_group_paid,
                'total_group_debt': total_group_debt,
                'students': student_list,
            })

        context.update({'years': years, 'months': months, 'month_debt_counts': month_debt_counts, 'groups': groups,
                        'selected_year': selected_year, 'selected_month': selected_month,
                        'selected_group_id': selected_group_id, 'group_data': group_data})
        return context


@csrf_exempt
def add_payment(request):
    """ O‘quvchiga to‘lov kiritish va cashback yaratish """

    print("\n🟢 [DEBUG] `add_payment` funksiyasi ishga tushdi...")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(f"📩 [DEBUG] Kelgan ma'lumotlar: {data}")

            student_id = data.get("student_id")
            group_id = data.get("group_id")

            try:
                amount_paid = int(data.get("amount_paid", 0))  # **Faqat butun son qabul qilish**
            except Exception as e:
                print(f"❌ [DEBUG] To‘lov summasi noto‘g‘ri: {e}")
                return JsonResponse({"success": False, "message": "To‘lov summasi noto‘g‘ri!"}, status=400)

            # **📌 Majburiy maydonlarni tekshirish**
            if not (student_id and group_id and amount_paid > 0):
                print("❌ [DEBUG] Xatolik: Barcha maydonlar to‘ldirilishi shart!")
                return JsonResponse({"success": False, "message": "Barcha maydonlar to‘ldirilishi shart!"}, status=400)

            # **📌 O‘quvchi va guruhni olish**
            student = get_object_or_404(SubmittedStudent, id=student_id)
            group = get_object_or_404(E_groups, id=group_id)
            print(f"✅ [DEBUG] Talaba: {student.first_name} {student.last_name}, Guruh: {group.group_name}")

            # **📌 Joriy oy uchun qarzdorlikni olish yoki yaratish**
            today = now().date()
            payment_record, created = PaymentRecord.objects.get_or_create(
                student=student, group=group, month=today.month, year=today.year,
                defaults=PaymentRecord.calculate_payment(student, group)
            )

            # **📌 To‘lovni saqlash**
            with transaction.atomic():
                payment_record.amount_paid += amount_paid
                payment_record.remaining_balance = max(payment_record.total_debt - payment_record.amount_paid, 0)

                if payment_record.remaining_balance < 100:
                    payment_record.remaining_balance = 0

                payment_record.save()
                print(f"✅ [DEBUG] Yangi to‘lov kiritildi: {amount_paid} so‘m | Qolgan qarz: {payment_record.remaining_balance}")

                # **📌 Agar qarzdorlik yopilgan bo‘lsa, `SubmittedStudent` holatini `paid`ga o‘zgartirish**
                if payment_record.remaining_balance == 0:
                    student.status = "paid"
                    student.save()
                    print("✅ [DEBUG] Talabaning holati 'paid' ga o‘zgartirildi.")

                # **📌 O‘qituvchiga cashback hisoblash (10%)**
                teacher = student.added_by
                teacher_cashback_amount = (amount_paid * 10) // 100  # **Butun son olish uchun `//` ishlatilgan**

                if teacher and teacher.user_type == "2":  # Faqat o‘qituvchilar uchun cashback
                    cashback, _ = Cashback.objects.get_or_create(
                        name="Kurs uchun to‘lov",
                        type="3",
                        user_type="2",
                        is_active=True
                    )

                    cashback_record, created = CashbackRecord.objects.get_or_create(
                        cashback=cashback,
                        teacher=teacher,
                        student=student,
                        defaults={"is_paid": False}
                    )
                    cashback_record.cashback.summasi += teacher_cashback_amount
                    cashback_record.cashback.save()
                    print(f"💰 [DEBUG] O‘qituvchiga cashback qo‘shildi: {teacher_cashback_amount} so‘m")

                # **📌 Maktab direktori uchun cashback hisoblash (5%)**
                school_director = None
                if teacher and teacher.maktab:
                    school_director = CustomUser.objects.filter(
                        maktab=teacher.maktab,  # O‘qituvchining maktabi
                        user_type="3"  # Direktor user_type=3
                    ).first()

                director_cashback_amount = (amount_paid * 5) // 100  # **Butun son olish uchun `//` ishlatilgan**

                if school_director:
                    director_cashback, _ = Cashback.objects.get_or_create(
                        name="Maktab direktori cashback",
                        type="5",
                        user_type="3",
                        is_active=True
                    )

                    director_cashback_record, created = CashbackRecord.objects.get_or_create(
                        cashback=director_cashback,
                        teacher=school_director,
                        student=student,
                        defaults={"is_paid": False}
                    )
                    director_cashback_record.cashback.summasi += director_cashback_amount
                    director_cashback_record.cashback.save()
                    print(f"💰 [DEBUG] Direktorga cashback qo‘shildi: {director_cashback_amount} so‘m")

            return JsonResponse({
                "success": True,
                "message": f"{student.first_name} {student.last_name} uchun {amount_paid} so‘m to‘landi!",
                "total_paid": payment_record.amount_paid,
                "remaining_balance": payment_record.remaining_balance,
                "student_status": student.status,
                "teacher_cashback": teacher_cashback_amount,
                "director_cashback": director_cashback_amount if school_director else 0
            })

        except Exception as e:
            print(f"❌ [DEBUG] Xatolik yuz berdi: {str(e)}")
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    print("❌ [DEBUG] Xato so‘rov turi!")
    return JsonResponse({"success": False, "message": "Xato so‘rov turi!"}, status=400)

class BlockStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context


class StatisticsStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # **1️⃣ O‘quvchilar statistikasi**
        students = SubmittedStudent.objects.annotate(
            total_debt=Sum('paymentrecord__remaining_balance'),
            total_paid=Sum('paymentrecord__amount_paid'),
            teacher_name=Concat(
                F('added_by__first_name'),
                Value(' '),
                F('added_by__last_name'),
                output_field=CharField()
            )
        )
        context['students'] = students
        context['total_students'] = students.count()
        context['paid_students'] = students.filter(status='paid').count()
        context['debt_students'] = students.exclude(status='paid').count()

        # **2️⃣ Guruhlar statistikasi**
        groups = E_groups.objects.annotate(
            student_count=Count('students'),
            total_expected=Sum('students__paymentrecord__total_debt'),
            total_remaining=Sum('students__paymentrecord__remaining_balance')
        )
        context['groups'] = groups
        context['total_groups'] = groups.count()
        context['active_groups'] = groups.filter(is_active=True).count()
        context['inactive_groups'] = groups.filter(is_active=False).count()

        # **3️⃣ Kurslar statistikasi**
        courses = Kurs.objects.annotate(
            student_count=Count('submitted_students'),
            group_count=Count('groups'),
            total_income=Sum('submitted_students__paymentrecord__amount_paid'),
            total_debt=Sum('submitted_students__paymentrecord__remaining_balance')
        )
        context['courses'] = courses
        context['total_courses'] = courses.count()

        # **4️⃣ Yillik tushum statistikasi**
        current_year = datetime.now().year
        monthly_payments = PaymentRecord.objects.filter(year=current_year).values('month').annotate(
            total=Sum('amount_paid'),
            unpaid_students=Count('student', filter=Q(remaining_balance__gt=0)),
            paid_students=Count('student', filter=Q(remaining_balance=0))
        ).order_by('month')
        context['monthly_payments'] = monthly_payments

        # **5️⃣ O‘qituvchilar statistikasi**
        teachers = CustomUser.objects.filter(submittedstudent__isnull=False).annotate(
            student_count=Count('submittedstudent')
        )
        context['teachers'] = teachers

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
