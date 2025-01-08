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


class CoursesView(TemplateView):

    def get_context_data(self, **kwargs):
        """
        Prepares context data for the template with detailed information about courses.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Get the current user
        user = self.request.user

        # Fetch centers associated with the user (as a leader or admin)
        user_centers = Center.objects.filter(rahbari=user) | Center.objects.filter(filial__admins=user)

        if not user_centers.exists():
            context.update({
                'error': "Sizga biriktirilgan markaz mavjud emas.",
                'kurslar': [],
            })
            return context

        # Search query for filtering courses
        search_query = self.request.GET.get('q', '').strip()

        # Fetch courses associated with the centers
        kurslar = Kurs.objects.filter(center__in=user_centers)
        if search_query:
            kurslar = kurslar.filter(nomi__icontains=search_query)

        kurslar = kurslar.order_by('-created_at')

        # Format course data for the context
        kurslar_data = []
        for kurs in kurslar:
            # Calculate group and student counts for each course
            groups = kurs.groups.all()
            group_count = groups.count()
            student_count = sum(group.students.count() for group in groups)

            # Add formatted price
            narxi_formatted = number_format(kurs.narxi, use_l10n=True, force_grouping=True)

            kurslar_data.append({
                "id": kurs.id,
                "nomi": kurs.nomi,
                "narxi": kurs.narxi,
                "narxi_formatted": narxi_formatted,
                "group_count": group_count,
                "student_count": student_count,
                "created_at": kurs.created_at,
                "updated_at": kurs.updated_at,
                "is_active": kurs.is_active,
            })

        # Update context with course data and search query
        context.update({
            'kurslar': kurslar_data,
            'kurslar_count': kurslar.count(),
            'search_query': search_query,
        })

        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles the creation of a new course with validation.
        """
        nomi = request.POST.get("nomi", "").strip()
        narxi = request.POST.get("narxi", "").strip()

        if not nomi:
            return JsonResponse({"success": False, "message": "Kurs nomi kiritilishi kerak."}, status=400)
        if not narxi or not narxi.isdigit() or int(narxi) <= 0:
            return JsonResponse({"success": False, "message": "Kurs narxi to'g'ri kiritilishi kerak."}, status=400)

        try:
            user_centers = Center.objects.filter(rahbari=request.user) | Center.objects.filter(
                filial__admins=request.user)

            if not user_centers.exists():
                return JsonResponse({"success": False, "message": "Sizga biriktirilgan markaz mavjud emas."},
                                    status=403)

            center = user_centers.first()
            normalized_nomi = nomi[0].upper() + nomi[1:].lower()

            if Kurs.objects.filter(center=center, nomi__iexact=normalized_nomi).exists():
                return JsonResponse({"success": False, "message": f"'{normalized_nomi}' nomli kurs allaqachon mavjud."},
                                    status=400)

            kurs = Kurs.objects.create(
                center=center,
                nomi=normalized_nomi,
                narxi=int(narxi),
                is_active=True
            )

            return JsonResponse({"success": True, "message": f"'{kurs.nomi}' kursi muvaffaqiyatli qo'shildi."})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    def delete(self, request, *args, **kwargs):
        """
        Handles the deletion of a course.
        """
        kurs_id = kwargs.get("pk")
        try:
            # Get the course object associated with the current user
            kurs = get_object_or_404(
                Kurs,
                id=kurs_id,
                center__in=Center.objects.filter(rahbari=request.user) | Center.objects.filter(
                    filial__admins=request.user)
            )

            # Check if the course is associated with any groups
            if kurs.groups.exists():
                return JsonResponse(
                    {"success": False, "message": "Ushbu kursga guruhlar birikkan, o'chirib bo'lmaydi."}, status=400)

            # Check if the course is associated with any Yonalish
            if kurs.yonalishlar.exists():
                yonalish_names = ", ".join(yonalish.nomi for yonalish in kurs.yonalishlar.all())
                return JsonResponse(
                    {"success": False,
                     "message": f"Ushbu kurs quyidagi yo'nalish(lar)ga birikkan: {yonalish_names}. O'chirib bo'lmaydi."},
                    status=400
                )

            # If no associations exist, delete the course
            kurs.delete()
            return JsonResponse({"success": True, "message": "Kurs muvaffaqiyatli o'chirildi."})

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    def patch(self, request, *args, **kwargs):
        """
        Handles the editing of a course.
        """
        kurs_id = kwargs.get("pk")
        try:
            data = json.loads(request.body)
            nomi = data.get("nomi", "").strip()
            narxi = data.get("narxi", "").strip()

            if not nomi or not narxi:
                return JsonResponse({"success": False, "message": "Kurs nomi va narxi kiritilishi kerak."}, status=400)
            if not narxi.isdigit() or int(narxi) <= 0:
                return JsonResponse({"success": False, "message": "Kurs narxi to'g'ri kiritilishi kerak."}, status=400)

            kurs = get_object_or_404(Kurs, id=kurs_id,
                                     center__in=Center.objects.filter(rahbari=request.user) | Center.objects.filter(
                                         filial__admins=request.user))

            kurs.nomi = nomi[0].upper() + nomi[1:].lower()
            kurs.narxi = int(narxi)
            kurs.save()

            return JsonResponse({"success": True, "message": "Kurs muvaffaqiyatli tahrirlandi."})

        except Kurs.DoesNotExist:
            return JsonResponse({"success": False, "message": "Kurs topilmadi."}, status=404)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)
