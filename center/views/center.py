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


class CenterView(TemplateView):
    def get_context_data(self, **kwargs):
        # Initialize the base context using TemplateLayout
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Foydalanuvchi obyektini olish
        user = self.request.user

        # Center obyektlari
        centers = Center.objects.all()

        # Userga tegishli submitted students
        submitted_students = (
            SubmittedStudent.objects.filter(added_by=user)
            if user.is_authenticated
            else SubmittedStudent.objects.none()
        )

        # Barcha submitted students
        all_submitted_students = SubmittedStudent.objects.all()

        # Faqat SubmittedStudent orqali mavjud maktablarni olish
        school_ids = SubmittedStudent.objects.filter(sinf__maktab__isnull=False).values_list('sinf__maktab',
                                                                                             flat=True).distinct()
        schools = Maktab.objects.filter(id__in=school_ids)

        # Qo'shimcha kerakli contextlar
        teachers = CustomUser.objects.filter(now_role="2")  # O'qituvchilar
        sinflar = Sinf.objects.all()  # Sinflar
        kasblar = Kasb.objects.all()  # Kasblar
        yonalishlar = Yonalish.objects.all()  # Yo'nalishlar

        # Add data to context
        context.update({
            'centers': centers,
            'grades': range(1, 12),  # 1-dan 11-gacha
            'submitted_students': submitted_students,  # Userga tegishli
            'all_submitted_students': all_submitted_students,  # Barcha submitted students
            'teachers': teachers,  # O'qituvchilar
            'schools': schools,  # Filterlangan maktablar
            'sinflar': sinflar,  # Sinflar
            'kasblar': kasblar,  # Kasblar
            'yonalishlar': yonalishlar,  # Yo'nalishlar
        })

        return context


class CenterDetailView(LoginRequiredMixin, DetailView):
    model = Center
    context_object_name = "center"
    template_name = "center_detail.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Filiallar
        context["filials"] = Filial.objects.filter(center=self.object)

        # Kasblar
        context["kasblar"] = Kasb.objects.filter(center=self.object)

        # Yo'nalishlar
        context["yonalishlar"] = Yonalish.objects.filter(center=self.object)

        # Kurslar
        context["kurslar"] = Kurs.objects.filter(center=self.object)

        # E-guruhlar
        context["e_groups"] = E_groups.objects.filter(kurs__center=self.object)

        # Yuborilgan o'quvchilar
        context["submitted_students"] = SubmittedStudent.objects.filter(filial__center=self.object)

        # Maktablar
        context[
            "maktablar"] = self.object.maktab.all()  # Center bilan ManyToManyField orqali bog'langan barcha maktablar

        # Sinflar
        sinf_list = Sinf.objects.filter(maktab__in=self.object.maktab.all())
        context["sinflar"] = sinf_list

        return context