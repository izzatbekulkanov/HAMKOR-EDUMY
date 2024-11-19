from django.http import JsonResponse
from django.views import View
from center.models import Center, Filial


class GetCentersWithFilialsView(View):
    """
    Barcha o'quv markazlari va ularning filiallari sonini JSON formatda qaytaruvchi klass.
    """

    def get(self, request, *args, **kwargs):
        try:
            centers = Center.objects.all()
            data = []

            for center in centers:
                filials_count = Filial.objects.filter(center=center).count()
                data.append({
                    "center_id": center.id,
                    "center_name": center.nomi,
                    "admin_name": center.rahbari.get_full_name() if center.rahbari else "Belgilanmagan",
                    "admin_phone": center.rahbari.phone_number if center.rahbari and center.rahbari.phone_number else "Noma'lum",
                    "filials_count": filials_count,
                })

            return JsonResponse({"success": True, "data": data}, status=200)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


class GetCenterDetailsView(View):
    """
    View to fetch detailed information about a specific center, including its filials.
    """

    def get(self, request, center_id, *args, **kwargs):
        try:
            # Fetch the center by ID
            center = Center.objects.get(id=center_id)

            # Get all filials related to the center
            filials = Filial.objects.filter(center=center)

            # Prepare the response data for the center
            filials_data = []
            for filial in filials:
                # Prepare data for each filial
                images_data = []
                for image in filial.images.all():
                    images_data.append({
                        "id": image.id,
                        "title": image.title,
                        "description": image.description,
                        "image_url": image.image.url if image.image else None,
                    })

                filials_data.append({
                    "id": filial.id,
                    "location": filial.location or "Mavjud emas",
                    "contact": filial.contact or "Mavjud emas",
                    "telegram": filial.telegram or "Mavjud emas",
                    "image_url": filial.image.url if filial.image else None,
                    "additional_images": images_data,
                })

            # Prepare center data
            data = {
                "center_id": center.id,
                "center_name": center.nomi,
                "admin_name": center.rahbari.get_full_name() if center.rahbari else "Belgilanmagan",
                "admin_phone": center.rahbari.phone_number if center.rahbari and center.rahbari.phone_number else "Noma'lum",
                "filials_count": filials.count(),
                "address": getattr(center, "address", None) or "Mavjud emas",  # Assuming `address` field exists
                "extra_contact": getattr(center, "extra_contact", None) or "Mavjud emas",
                # Assuming `extra_contact` exists
                "filials": filials_data,  # Include filial details
            }

            return JsonResponse({"success": True, "data": data}, status=200)

        except Center.DoesNotExist:
            return JsonResponse({"success": False, "message": "O'quv markazi topilmadi."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)
