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

class LearningGroupView(TemplateView):
    template_name = "learning_groups.html"

    def get_context_data(self, **kwargs):
        """
        Prepares the context data for groups and courses associated with the user.
        """
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        # Get the current user
        user = self.request.user

        # Fetch centers associated with the user (as a leader or admin)
        rahbar_center = Center.objects.filter(rahbari=user).first()
        filial_centers = Center.objects.filter(filial__admins=user).distinct()
        centers = set()
        if rahbar_center:
            centers.add(rahbar_center)
        centers.update(filial_centers)

        if not centers:
            context.update({
                'error': "Sizga biriktirilgan markaz mavjud emas.",
                'guruhlar': [],
                'kurslar': [],
                'statistics': {},
                'days_of_week': [],
            })
            return context

        # Fetch groups and courses associated with the centers
        groups = E_groups.objects.filter(center__in=centers).order_by('-created_at')
        kurslar = Kurs.objects.filter(center__in=centers).order_by('nomi')

        # Format course data for the dropdown
        kurslar_data = [{"id": kurs.id, "nomi": kurs.nomi} for kurs in kurslar]

        # Initialize statistics
        total_groups = groups.count()
        active_groups = groups.filter(is_active=True).count()
        inactive_groups = total_groups - active_groups
        linked_groups = groups.filter(kurs__isnull=False).count()
        unlinked_groups = total_groups - linked_groups
        total_students = sum(group.students.count() for group in groups)

        # Format group data for the table
        groups_data = []
        for group in groups:
            students_count = group.students.count()
            kurs_name = group.kurs.nomi if group.kurs else "Biriktirilmagan"
            kurs_id = group.kurs.id if group.kurs else None
            groups_data.append({
                "id": group.id,
                "group_name": group.group_name,
                "kurs_name": kurs_name,
                "kurs_id": kurs_id,
                "students_count": students_count,
                "days_of_week": group.days_of_week,  # JSON massiv sifatida uzatish
                "created_at": group.created_at,
                "updated_at": group.updated_at,
                "is_active": group.is_active,
            })

        # Add days of week mapping
        days_of_week = E_groups.DAYS_OF_WEEK

        # Add all data to the context
        context.update({
            'guruhlar': groups_data,
            'kurslar': kurslar_data,
            'guruhlar_count': total_groups,
            'days_of_week': days_of_week,  # Full week days list
            'statistics': {
                'total_groups': total_groups,
                'active_groups': active_groups,
                'inactive_groups': inactive_groups,
                'linked_groups': linked_groups,
                'unlinked_groups': unlinked_groups,
                'total_students': total_students,
            },
        })

        return context

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles the creation of a new group with validation.
        """
        try:
            data = json.loads(request.body)

            group_name = data.get('group_name', '').strip()
            kurs_id = data.get('kurs')
            days_of_week = data.get('days_of_week', [])

            # Validate inputs
            if not group_name:
                return JsonResponse({"success": False, "message": "Guruh nomi kiritilishi kerak."}, status=400)
            if not kurs_id:
                return JsonResponse({"success": False, "message": "Kursni tanlang."}, status=400)
            if not days_of_week:
                return JsonResponse({"success": False, "message": "Dars kunlarini tanlang."}, status=400)

            # Get the course
            kurs = Kurs.objects.filter(id=kurs_id, center__rahbari=request.user) | \
                   Kurs.objects.filter(id=kurs_id, center__filial__admins=request.user)
            kurs = kurs.first()
            if not kurs:
                return JsonResponse({"success": False, "message": "Tanlangan kurs mavjud emas yoki ruxsat yo'q."},
                                    status=403)

            # Check if the group already exists
            if E_groups.objects.filter(group_name__iexact=group_name, kurs=kurs).exists():
                return JsonResponse({"success": False, "message": "Bunday nomdagi guruh allaqachon mavjud."},
                                    status=400)

            # Create the new group
            new_group = E_groups.objects.create(
                group_name=group_name,
                kurs=kurs,
                days_of_week=days_of_week,
                center=kurs.center
            )

            return JsonResponse(
                {"success": True, "message": f"'{new_group.group_name}' guruh muvaffaqiyatli qo'shildi."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Yaroqli ma'lumot yuborilmadi."}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def patch(self, request, *args, **kwargs):
        try:
            group_id = kwargs.get('pk')
            print(f"[DEBUG] Group ID: {group_id}")

            group = E_groups.objects.get(id=group_id)
            print(f"[DEBUG] Retrieved Group: {group}")

            data = json.loads(request.body)
            print(f"[DEBUG] Received Data: {data}")

            group_name = data.get('group_name', '').strip()
            kurs_id = data.get('kurs')

            print(f"[DEBUG] Parsed Data - Group Name: {group_name}, Kurs ID: {kurs_id}")

            if not group_name or not kurs_id:
                print("[DEBUG] Missing required fields")
                return JsonResponse({"success": False, "message": "Barcha maydonlar to'ldirilishi shart."}, status=400)

            kurs = Kurs.objects.filter(id=kurs_id, center=group.center).first()
            if not kurs:
                print("[DEBUG] Kurs not found or unauthorized access")
                return JsonResponse({"success": False, "message": "Kurs topilmadi yoki ruxsat yo'q."}, status=403)

            # Yangi tanlangan kunlar asosida yangilash
            group.group_name = group_name
            group.kurs = kurs
            group.save()

            print(f"[DEBUG] Group Updated Successfully: {group}")
            return JsonResponse({"success": True, "message": f"Guruh '{group.group_name}' muvaffaqiyatli yangilandi."})

        except E_groups.DoesNotExist:
            print("[DEBUG] Group not found")
            return JsonResponse({"success": False, "message": "Guruh topilmadi."}, status=404)
        except Exception as e:
            print(f"[DEBUG] Exception Occurred: {str(e)}")
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            group_id = kwargs.get('pk')  # URL dan guruh ID sini olish
            print(f"[DEBUG] Delete Group ID: {group_id}")

            group = E_groups.objects.get(id=group_id)  # Guruhni topish
            print(f"[DEBUG] Retrieved Group for Deletion: {group}")

            # Guruhda o‘quvchilar borligini tekshirish
            if group.students.exists():
                print("[DEBUG] Group has students. Deletion denied.")
                return JsonResponse(
                    {"success": False, "message": "Guruhga o'quvchilar biriktirilganligi sababli o'chirib bo'lmaydi."},
                    status=400)

            # Guruhni o‘chirish
            group.delete()

            print(f"[DEBUG] Group Deleted Successfully: {group_id}")
            return JsonResponse({"success": True, "message": f"Guruh muvaffaqiyatli o'chirildi."})

        except E_groups.DoesNotExist:
            print("[DEBUG] Group not found")
            return JsonResponse({"success": False, "message": "Guruh topilmadi."}, status=404)

        except Exception as e:
            print(f"[DEBUG] Exception Occurred: {str(e)}")
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


@csrf_exempt
def add_or_remove_day(request, group_id):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
            day = data.get('day')

            if not day:
                return JsonResponse({'success': False, 'message': 'Hafta kuni ko\'rsatilmagan.'}, status=400)

            group = E_groups.objects.get(id=group_id)

            if day in group.days_of_week:
                group.days_of_week.remove(day)
                action = 'guruhdan olib tashlandi'
            else:
                group.days_of_week.append(day)
                action = 'guruhga qo\'shildi'

            group.save()

            return JsonResponse({
                'success': True,
                'message': f"'{day}' hafta kuni  {action} ."
            })

        except E_groups.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Guruh topilmadi.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Xatolik yuz berdi: {str(e)}"}, status=500)

    return JsonResponse({'success': False, 'message': 'Faoliyat turi noto\'g\'ri.'}, status=405)