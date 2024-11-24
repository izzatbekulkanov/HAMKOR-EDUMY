from django.db.models import Count
from django.views import View
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt

from school.models import Sinf, Maktab, Belgisi
import json


@csrf_exempt
def add_class(request):
    """
    Add a new class (Sinf) associated with a school (Maktab) and optional badge (Belgisi).
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data

            # Extract data from the request
            maktab_id = data.get("maktab_id")
            sinf_raqami = data.get("sinf_raqami")
            belgisi_nomi = data.get("belgisi")

            # Validate mandatory fields
            if not (maktab_id and sinf_raqami):
                return JsonResponse({"error": "Maktab ID va sinf raqami majburiy."}, status=400)

            # Get the related Maktab
            try:
                maktab = Maktab.objects.get(id=maktab_id)
            except Maktab.DoesNotExist:
                return JsonResponse({"error": "Maktab topilmadi."}, status=404)

            # Handle badge creation or assignment
            belgisi = None
            if belgisi_nomi:
                belgisi, _ = Belgisi.objects.get_or_create(nomi=belgisi_nomi.strip().upper())

            # Create the Sinf
            sinf = Sinf.objects.create(
                maktab=maktab,
                sinf_raqami=sinf_raqami.strip(),
                belgisi=belgisi
            )

            return JsonResponse({"message": "Sinf muvaffaqiyatli qo'shildi.", "id": sinf.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Server xatosi: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)


class StatsClassAPIView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Calculate statistics
            total_classes = Sinf.objects.count()
            total_schools = Maktab.objects.count()

            # Group classes by viloyat, tuman, and maktab
            grouped_data = (
                Sinf.objects
                .select_related('maktab', 'belgisi')
                .values('maktab__viloyat', 'maktab__tuman', 'maktab__id', 'maktab__nomi')
                .annotate(class_count=Count('id'))
                .order_by('maktab__viloyat', 'maktab__tuman', 'maktab__nomi')
            )

            # Structure the result
            grouped_result = {}
            for entry in grouped_data:
                viloyat = entry['maktab__viloyat']
                tuman = entry['maktab__tuman']
                maktab = {
                    "id": entry['maktab__id'],
                    "nomi": entry['maktab__nomi'],
                    "class_count": entry['class_count']
                }

                if viloyat not in grouped_result:
                    grouped_result[viloyat] = {}
                if tuman not in grouped_result[viloyat]:
                    grouped_result[viloyat][tuman] = []

                grouped_result[viloyat][tuman].append(maktab)

            return JsonResponse({
                'success': True,
                'stats': {
                    'total_classes': total_classes,
                    'total_schools': total_schools
                },
                'grouped_classes': grouped_result
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f"Xatolik yuz berdi: {str(e)}"
            }, status=500)

