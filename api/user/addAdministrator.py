from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import authenticate, login
from account.models import CustomUser, Regions, District, Quarters, Gender, Roles  # Add Roles model
from school.models import Maktab


class AddAdministratorView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Extract data from the request
            first_name = request.POST.get('first_name', '').strip()
            second_name = request.POST.get('second_name', '').strip()
            third_name = request.POST.get('third_name', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            birth_date = request.POST.get('birth_date', '').strip()
            passport_serial = request.POST.get('passport_serial', '').strip()
            passport_jshshir = request.POST.get('passport_jshshir', '').strip()
            telegram = request.POST.get('telegram', '').strip()
            instagram = request.POST.get('instagram', '').strip()
            facebook = request.POST.get('facebook', '').strip()
            roles = request.POST.get('roles', '').strip()
            school_id = request.POST.get('school', '').strip()  # Get school ID
            password = request.POST.get('password', '').strip()

            # Validation
            if not all([first_name, second_name, username, email, phone_number, password]):
                return JsonResponse({'success': False, 'message': 'Barcha maydonlar to‘ldirilishi kerak!'})

            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'success': False, 'message': 'Noto‘g‘ri email manzili!'})

            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'Bu foydalanuvchi nomi band!'})

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Bu email band!'})

            # Ensure Gender model contains "Erkak" and "Ayol"
            male_gender, _ = Gender.objects.get_or_create(name="Erkak")
            female_gender, _ = Gender.objects.get_or_create(name="Ayol")

            # Determine gender based on second_name
            gender = male_gender if second_name.endswith("v") else female_gender if second_name.endswith(
                "va") else None

            if not gender:
                return JsonResponse({'success': False, 'message': 'Jinsni aniqlashda xatolik yuz berdi!'})

            # Fetch school object if provided
            school = None
            if school_id:
                try:
                    school = Maktab.objects.get(id=school_id)
                except Maktab.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Maktab topilmadi!'})

            # Create user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                second_name=second_name,
                third_name=third_name,
                phone_number=phone_number,
                birth_date=birth_date,
                passport_serial=passport_serial,
                passport_jshshir=passport_jshshir,
                telegram=telegram,
                instagram=instagram,
                facebook=facebook,
                now_role=str(roles),
                gender=gender, # Set the now_role field
                user_type=roles,  # Save as CEO_Administrator in user_type
                added_by=request.user,  # Qo'shgan foydalanuvchini saqlash
                password_save=password,  # Save plain text password
                maktab=school  # Assign school
            )

            # Authenticate and log in the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                return JsonResponse({'success': True, 'message': 'Foydalanuvchi muvaffaqiyatli qo‘shildi va tizimga kirdi!'})

            return JsonResponse({'success': False, 'message': 'Foydalanuvchi yaratilgan, lekin tizimga kira olmadi!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Xatolik yuz berdi: {str(e)}'})

