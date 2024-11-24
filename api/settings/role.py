# account/views.py
from django.http import JsonResponse
from django.views import View
from account.models import Roles


class SaveRolesView(View):
    def post(self, request):
        # AJAX so'rov orqali rollarni olish
        raw_roles = request.POST.getlist('roles[]', [])

        # Rollarni bo'sh bo'lishini tekshirish
        if raw_roles:
            selected_roles = raw_roles[0].split(',')
        else:
            selected_roles = []

        # Rol kodlarini odam tushunarli nomlarga mapping qilish
        role_mappings = {
            "ceo_administrator": "Bosh admin",
            "administrator": "Kichik admin",
            "partner": "Hamkor",
            "director": "Direktor",
            "student": "O'quvchi"
        }

        # Saqlangan rollar ro'yxatini kuzatish uchun
        created_roles = []

        # Har bir rol uchun iteratsiya qilish
        for role_code in selected_roles:
            role_code = role_code.strip()  # Qo'shimcha bo'sh joylarni olib tashlash
            role_name = role_mappings.get(role_code, role_code)  # Agar mapping mavjud bo'lmasa, code'dan foydalanish

            # Mavjudligini tekshirish va agar yo'q bo'lsa yaratish
            role, created = Roles.objects.get_or_create(code=role_code, defaults={'name': role_name})
            if created:
                created_roles.append(f"{role_name} (ID: {role.id})")  # Rol nomi va ID ni qo'shish

        # Javobni qaytarish
        return JsonResponse({
            "status": "success",
            "message": "Yangi rollar muvaffaqiyatli saqlandi",
            "created_roles": created_roles
        })


class RolesWithUsersView(View):
    def get(self, request):
        # Barcha rollarni olish
        roles = Roles.objects.all()

        # Har bir rol uchun foydalanuvchilarni olish
        roles_with_users = []
        for role in roles:
            # Rolga biriktirilgan foydalanuvchilar ro'yxati
            users = role.customuser_set.all()
            users_data = [{
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "second_name": user.second_name,
                "third_name": user.third_name,
                "user_type": user.get_user_type_display(),
            } for user in users]

            # Rol va foydalanuvchilar ma'lumotlarini lug'atga qo'shish
            roles_with_users.append({
                "role_id": role.id,
                "role_code": role.code,
                "role_name": role.name,
                "users": users_data,
            })

        # Ma'lumotlarni JSON formatida qaytarish
        return JsonResponse({
            "status": "success",
            "roles": roles_with_users
        })
