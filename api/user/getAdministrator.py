from django.http import JsonResponse
from django.views import View
from account.models import CustomUser


class GetAdministratorsView(View):
    def get(self, request, *args, **kwargs):
        try:
            search_name = request.GET.get('searchName', '').strip()
            filter_gender = request.GET.get('filterGender', '').strip()
            filter_status = request.GET.get('filterStatus', '').strip()

            # Foydalanuvchilarni filtrlash
            administrators = CustomUser.objects.filter(user_type="5")
            if search_name:
                administrators = administrators.filter(first_name__icontains=search_name)
            if filter_gender:
                gender_filter = {'male': 'Erkak', 'female': 'Ayol'}.get(filter_gender, '')
                administrators = administrators.filter(gender__name=gender_filter)
            if filter_status:
                is_active = filter_status == 'active'
                administrators = administrators.filter(is_active=is_active)

            # Ma'lumotlarni JSON formatda tayyorlash
            data = [
                {
                    "id": admin.id,
                    "username": admin.username,
                    "email": admin.email,
                    "first_name": admin.first_name,
                    "second_name": admin.second_name,
                    "third_name": admin.third_name,
                    "phone_number": admin.phone_number,
                    "birth_date": admin.birth_date,
                    "gender__name": admin.gender.name if admin.gender else "",
                    "regions": admin.regions.name if admin.regions else "",
                    "district": admin.district.name if admin.district else "",
                    "quarters": admin.quarters.name if admin.quarters else "",
                    "address": admin.address,
                    "passport_serial": admin.passport_serial,
                    "passport_jshshir": admin.passport_jshshir,
                    "telegram": admin.telegram,
                    "instagram": admin.instagram,
                    "facebook": admin.facebook,
                    "is_active": admin.is_active,
                    "now_role": admin.now_role,
                    "user_type": admin.get_user_type_display(),  # Turi (matn ko‘rinishida)
                    "last_login": admin.last_login.strftime('%d.%m.%Y | %H:%M') if admin.last_login else "",
                    "last_logout": admin.last_logout,
                    "created_at": admin.created_at,
                    "updated_at": admin.updated_at,
                }
                for admin in administrators
            ]

            # JSON formatda ma'lumotlarni qaytarish
            return JsonResponse({'success': True, 'data': data}, safe=False)

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Xatolik yuz berdi: {str(e)}'})


class GetAdminsView(View):
    def get(self, request, *args, **kwargs):
        admins = CustomUser.objects.filter(is_active=True, user_type='5')
        data = [{'id': admin.id, 'full_name': admin.get_full_name(), 'phone_number': admin.phone_number} for admin in admins]
        return JsonResponse({'success': True, 'data': data})
