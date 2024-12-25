import phonenumbers
from django.db.models import Q
from django.http import JsonResponse
from django.views import View
from account.models import CustomUser
from center.models import Center, Filial

from django.db.models import Q

def format_phone_number(phone_number):
    try:
        # Raqamni analiz qilish
        parsed_number = phonenumbers.parse(phone_number, "UZ")
        # Formatlash
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except phonenumbers.NumberParseException:
        # Agar raqam noto'g'ri bo'lsa, asl raqamni qaytaradi
        return phone_number

class GetAdministratorsView(View):
    def get(self, request, *args, **kwargs):
        try:
            search_name = request.GET.get('searchName', '').strip()
            filter_gender = request.GET.get('filterGender', '').strip()
            filter_status = request.GET.get('filterStatus', '').strip()
            filter_role = request.GET.get('filterRole', '').strip()

            # Foydalanuvchini aniqlash
            current_user = request.user

            # Barcha foydalanuvchilarni olish
            administrators = CustomUser.objects.filter(is_active=True)

            if current_user.now_role == "6":
                # Superadmin bo'lsa barcha foydalanuvchilarni yuborish
                pass
            else:
                # Foydalanuvchiga bog'langan markaz va filial ma'lumotlarini olish
                user_centers = Center.objects.filter(rahbari=current_user)
                user_filials = Filial.objects.filter(center__in=user_centers)

                # Filtrlar
                administrators = administrators.filter(
                    Q(added_by=current_user) |  # Foydalanuvchi tomonidan kiritilganlar
                    Q(user_type__in=["2", "3"]) |  # O'qituvchilar va Direktorlar
                    Q(administered_filials__in=user_filials) |  # Foydalanuvchi filiallariga birikkanlar
                    Q(administered_filials__center__in=user_centers)  # Foydalanuvchi markaziga birikkanlar
                ).distinct()

            # Qo'shimcha filtrlash
            if filter_role:
                administrators = administrators.filter(user_type=filter_role)
            if search_name:
                administrators = administrators.filter(first_name__icontains=search_name)
            if filter_gender:
                gender_filter = {'male': 'Erkak', 'female': 'Ayol'}.get(filter_gender, '')
                administrators = administrators.filter(gender__name=gender_filter)
            if filter_status:
                is_active = filter_status == 'active'
                administrators = administrators.filter(is_verified=is_active)

            # Ma'lumotlarni JSON formatda tayyorlash
            data = [
                {
                    "id": admin.id,
                    "username": admin.username,
                    "email": admin.email,
                    "first_name": admin.first_name,
                    "second_name": admin.second_name,
                    "third_name": admin.third_name,
                    "phone_number": format_phone_number(admin.phone_number),  # Telefon raqamni formatlash
                    "birth_date": admin.birth_date,
                    "gender__name": admin.gender.name if admin.gender else "",
                    "passport_serial": admin.passport_serial,
                    "passport_jshshir": admin.passport_jshshir,
                    "now_password": admin.password_save,
                    "is_active": admin.is_active,
                    "is_verified": admin.is_verified,
                    "now_role": admin.get_user_type_display(),
                    "user_type": admin.get_user_type_display(),
                    "last_login": admin.last_login.strftime('%d.%m.%Y | %H:%M') if admin.last_login else "",
                    "last_logout": admin.last_logout,
                    "created_at": admin.created_at.strftime('%d.%m.%Y | %H:%M') if admin.last_login else "",
                    "updated_at": admin.updated_at.strftime('%d.%m.%Y | %H:%M') if admin.last_login else "",
                    "school": {
                        "id": admin.maktab.id if admin.maktab else None,
                        "viloyat": admin.maktab.viloyat if admin.maktab else "",
                        "tuman": admin.maktab.tuman if admin.maktab else "",
                        "nomi": admin.maktab.nomi if admin.maktab else "",
                        "raqami": admin.maktab.maktab_raqami if admin.maktab else "",

                    } if admin.maktab else None
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
