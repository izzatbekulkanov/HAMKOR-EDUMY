from urllib import request

from django.core.paginator import Paginator
from django.views.generic import TemplateView
from django.db.models import Q, Sum

from account.models import Cashback, CustomUser, CashbackRecord
from center.models import SubmittedStudent, Kasb, Yonalish, Kurs
from school.models import Sinf
from web_project import TemplateLayout


class DirectorStudentView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Filtering parametrlari
        query = self.request.GET.get("q", "")
        kasb_id = self.request.GET.get("kasb")
        yonalish_id = self.request.GET.get("yonalish")
        kurs_id = self.request.GET.get("kurs")

        school = self.request.user.maktab  # ✅ self.request ishlatildi

        student_sinf = Sinf.objects.filter(maktab=school)

        students = SubmittedStudent.objects.filter(sinf__in=student_sinf)


        if query:
            students = students.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )

        if kasb_id:
            students = students.filter(kasb_id=kasb_id)

        if yonalish_id:
            students = students.filter(yonalish_id=yonalish_id)

        if kurs_id:
            students = students.filter(kurslar__id=kurs_id).distinct()  # ✅ distinct() qo‘shildi

        # Pagination
        paginator = Paginator(students, 10)
        page_number = self.request.GET.get("page")
        students_page = paginator.get_page(page_number)

        context.update({
            "students": students_page,
            "kasblar": Kasb.objects.all(),
            "yonalishlar": Yonalish.objects.all(),
            "kurslar": Kurs.objects.all(),
        })
        return context

class DirectorCashbackView(TemplateView):

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # 🔹 Hozirgi direktor
        director = self.request.user

        # 🔹 Direktor boshqarayotgan maktab
        school = director.maktab

        # 🔹 Maktabdagi barcha o‘qituvchilar (user_type="2")
        teachers = CustomUser.objects.filter(maktab=school, user_type="2")

        # 🔹 O‘qituvchilarga tegishli barcha talabalar
        students = SubmittedStudent.objects.filter(added_by__in=teachers)

        # 🔹 Direktor ulushiga tushgan cashbacklar
        director_cashbacks = CashbackRecord.objects.filter(teacher=director)

        # 🔹 Talabalar orqali kelgan cashbacklar
        student_cashbacks = CashbackRecord.objects.filter(student__in=students)

        # 🔹 Kontekstga qo‘shish
        context.update({
            "director": director,
            "teachers": teachers,
            "students": students,
            "director_cashbacks": director_cashbacks,
            "student_cashbacks": student_cashbacks,
        })

        return context
