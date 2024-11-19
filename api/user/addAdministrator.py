from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import authenticate, login
from account.models import CustomUser, Regions, District, Quarters, Gender, Roles  # Add Roles model


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
            roles = request.POST.getlist('roles')
            password = request.POST.get('password', '').strip()
            region_id = request.POST.get('regions', '').strip()
            district_id = request.POST.get('district', '').strip()
            quarter_id = request.POST.get('quarters', '').strip()

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

            # Validate location fields
            region = Regions.objects.filter(id=region_id).first() if region_id else None
            district = District.objects.filter(id=district_id).first() if district_id else None
            quarter = Quarters.objects.filter(id=quarter_id).first() if quarter_id else None

            if region_id and not region:
                return JsonResponse({'success': False, 'message': 'Viloyat noto‘g‘ri tanlangan!'})
            if district_id and not district:
                return JsonResponse({'success': False, 'message': 'Tuman noto‘g‘ri tanlangan!'})
            if quarter_id and not quarter:
                return JsonResponse({'success': False, 'message': 'Mahalla noto‘g‘ri tanlangan!'})

            # Ensure Gender model contains "Erkak" and "Ayol"
            male_gender, _ = Gender.objects.get_or_create(name="Erkak")
            female_gender, _ = Gender.objects.get_or_create(name="Ayol")

            # Determine gender based on second_name
            gender = male_gender if second_name.endswith("v") else female_gender if second_name.endswith(
                "va") else None

            if not gender:
                return JsonResponse({'success': False, 'message': 'Jinsni aniqlashda xatolik yuz berdi!'})

            # Ensure "CEO_Administrator" role exists
            ceo_admin_role, _ = Roles.objects.get_or_create(name="CEO_Administrator")

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
                regions=region,
                district=district,
                quarters=quarter,
                gender=gender,
                now_role="CEO_Administrator",  # Set the now_role field
                user_type="5"  # Save as CEO_Administrator in user_type
            )

            # Assign roles
            if roles:
                user.roles.set(roles)

            # Authenticate and log in the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                return JsonResponse({'success': True, 'message': 'Foydalanuvchi muvaffaqiyatli qo‘shildi va tizimga kirdi!'})

            return JsonResponse({'success': False, 'message': 'Foydalanuvchi yaratilgan, lekin tizimga kira olmadi!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Xatolik yuz berdi: {str(e)}'})
