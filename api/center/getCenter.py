from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from center.models import Center, Filial
from school.models import Maktab


class GetCentersWithFilialsView(View):
    """
    Barcha o'quv markazlari va ularning filiallari sonini JSON formatda qaytaruvchi klass.
    """

    def get(self, request, *args, **kwargs):
        try:
            user = request.user  # Get the logged-in user
            data = []

            # Check if the user has now_role equal to 6 or is a superuser
            if user.now_role == '6' or user.is_superuser:
                # If user has role 6 or is superuser, return all centers
                centers = Center.objects.all()
            elif user.now_role == '2':
                # If user has role 2, return centers related to the user
                centers = Center.objects.filter(rahbari=user)
            else:
                # Otherwise, return only verified centers
                centers = Center.objects.filter(is_verified=True)

            # Loop through the centers
            for center in centers:
                filials_count = Filial.objects.filter(center=center).count()

                # Check if the admin exists and get the first_name, second_name
                if center.rahbari:
                    admin_first_name = center.rahbari.first_name
                    admin_second_name = center.rahbari.second_name
                    admin_full_name = center.rahbari.get_full_name()
                    admin_phone = center.rahbari.phone_number if center.rahbari.phone_number else "Noma'lum"
                else:
                    admin_first_name = "Belgilanmagan"
                    admin_second_name = "Belgilanmagan"
                    admin_full_name = "Belgilanmagan"
                    admin_phone = "Noma'lum"

                data.append({
                    "center_id": center.id,
                    "center_name": center.nomi,
                    "admin_first_name": admin_first_name,
                    "admin_last_name": admin_second_name,
                    "admin_full_name": admin_full_name,
                    "admin_phone": admin_phone,
                    "filials_count": filials_count,
                })

            return JsonResponse({"success": True, "data": data}, status=200)

        except Exception as e:
            return JsonResponse({"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}, status=500)


class GetCentersForTeacherView(View):
    """
    Foydalanuvchiga birikkan maktablarga bog'liq markazlar va all_views=True bo'lgan markazlarni qaytaruvchi klass.
    """

    def get(self, request, *args, **kwargs):
        try:
            user = request.user  # Joriy foydalanuvchini olish
            data = []

            # Foydalanuvchiga birikkan maktabni olish
            user_school = user.maktab

            # Foydalanuvchiga birikkan maktab orqali markazlarni olish
            centers = Center.objects.filter(
                Q(maktab=user_school) | Q(all_views=True),
                is_active=True,
                is_verified=True
            ).distinct()

            # Markaz ma'lumotlarini shakllantirish
            for center in centers:
                filials = Filial.objects.filter(center=center)

                # Filial ma'lumotlari
                filials_data = [
                    {
                        "branch_id": filial.id,
                        "branch_name": filial.location or "Noma'lum joylashuv",
                        "branch_contact": filial.contact or "Noma'lum aloqa",
                        "branch_admins": [
                            {"admin_id": admin.id, "admin_name": admin.get_full_name()}
                            for admin in filial.admins.all()
                        ],
                    }
                    for filial in filials
                ]

                # Admin ma'lumotlarini olish
                if center.rahbari:
                    admin_first_name = center.rahbari.first_name
                    admin_last_name = center.rahbari.last_name
                    admin_full_name = center.rahbari.get_full_name()
                    admin_phone = center.rahbari.phone_number if center.rahbari.phone_number else "Noma'lum"
                else:
                    admin_first_name = "Belgilanmagan"
                    admin_last_name = "Belgilanmagan"
                    admin_full_name = "Belgilanmagan"
                    admin_phone = "Noma'lum"

                # Markaz va filiallarni ma'lumotlariga qo'shish
                data.append({
                    "center_id": center.id,
                    "center_name": center.nomi,
                    "admin_first_name": admin_first_name,
                    "admin_last_name": admin_last_name,
                    "admin_full_name": admin_full_name,
                    "admin_phone": admin_phone,
                    "filials": filials_data,  # Filial ma'lumotlari
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
