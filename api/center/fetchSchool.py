import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from school.models import Maktab
from center.models import Center


class FetchSchoolsView(View):
    """
    Viloyat va tuman filtrlariga mos ravishda maktablarni olish uchun view.
    """

    def get(self, request, *args, **kwargs):
        center_id = request.GET.get("center_id")
        region = request.GET.get("region", "").strip()
        district = request.GET.get("district", "").strip()

        try:
            # Centerga birikkan maktablar
            assigned_school_ids = []
            if center_id:
                center = Center.objects.get(pk=center_id)
                assigned_school_ids = center.maktab.values_list('id', flat=True)

            # Agar viloyat va tuman mavjud bo'lsa, filtr asosida maktablarni olish
            if region and district:
                all_schools = Maktab.objects.exclude(id__in=assigned_school_ids)
                all_schools = all_schools.filter(viloyat=region, tuman=district)

                all_schools_data = [
                    {
                        "id": school.id,
                        "name": school.nomi,
                        "region": school.viloyat,
                        "district": school.tuman,
                        "school_number": school.maktab_raqami,
                    }
                    for school in all_schools
                ]
            else:
                # Viloyat yoki tuman bo'sh bo'lsa, maktablarni yubormaslik
                all_schools_data = []

            # Birikkan maktablar
            assigned_schools_data = []
            if center_id:
                assigned_schools = center.maktab.all()
                assigned_schools_data = [
                    {
                        "id": school.id,
                        "name": school.nomi,
                        "region": school.viloyat,
                        "district": school.tuman,
                        "school_number": school.maktab_raqami,
                    }
                    for school in assigned_schools
                ]

            # Dinamik viloyatlar va tumanlar
            regions = Maktab.objects.values_list('viloyat', flat=True).distinct()
            districts = (
                Maktab.objects.filter(viloyat=region).values_list('tuman', flat=True).distinct()
                if region else []
            )

            return JsonResponse({
                "success": True,
                "all_schools": all_schools_data,
                "assigned_schools": assigned_schools_data,
                "regions": list(regions),
                "districts": list(districts),
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": f"Xatolik yuz berdi: {str(e)}"
            }, status=500)


class AssignSchoolToCenterView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            center = Center.objects.get(pk=data["center_id"])
            school = Maktab.objects.get(pk=data["school_id"])
            center.maktab.add(school)
            return JsonResponse({"success": True}, status=200)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)


class UnassignSchoolFromCenterView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            center = Center.objects.get(pk=data["center_id"])
            school = Maktab.objects.get(pk=data["school_id"])
            center.maktab.remove(school)
            return JsonResponse({"success": True}, status=200)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=400)

