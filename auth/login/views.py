import json
import re
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from account.models import UserActivity
from auth.views import AuthView
from django.http import JsonResponse

CustomUser = get_user_model()  # CustomUser modelini olish


class LoginView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lsa, ularni asosiy sahifaga yo'naltirish
            return redirect("main-page-administrator")

        # Login sahifasini ko'rsatish
        return super().get(request)


@method_decorator(csrf_exempt, name='dispatch')
class DjangoAuthLoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            login_input = data.get("login_input")
            password = data.get("password")

            print(f"Kelgan ma'lumotlar: login_input={login_input}, password=****")

            if not login_input or not password:
                print("Xatolik: Login yoki parol kiritilmagan.")
                return JsonResponse({"error": "Login yoki parol kiritilishi shart."}, status=400)

            # Telefon raqamni formatlash
            if login_input.startswith("+998"):
                login_input = login_input.replace("+998", "998").replace(" ", "")
                print(f"Telefon raqam formatlandi: {login_input}")
            elif login_input.startswith("998"):
                login_input = login_input.replace(" ", "")
                print(f"Telefon raqam formatlandi: {login_input}")

            # Login turini aniqlash: email yoki username
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            login_field = 'email' if re.match(email_regex, login_input) else 'username'
            print(f"Aniqlangan login turi: {login_field}")

            # Foydalanuvchini olish
            user = None
            if login_field == 'email':
                user = CustomUser.objects.filter(email=login_input).first()
            else:
                user = CustomUser.objects.filter(username=login_input).first()

            if not user:
                print(f"Xatolik: Foydalanuvchi topilmadi: {login_input}")
                return JsonResponse({"error": "Login yoki parol noto'g'ri."}, status=401)

            print(f"Foydalanuvchi topildi: {user}")

            # Foydalanuvchini autentifikatsiya qilish
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user:
                print(f"Autentifikatsiya muvaffaqiyatli: {authenticated_user}")

                # Login qilish
                login(request, authenticated_user)

                # Foydalanuvchi faoliyatini logga yozish
                # UserActivity modeliga yangi yozuv qo'shish
                UserActivity.objects.create(user=authenticated_user, login_time=timezone.now())

                print("Foydalanuvchi tizimga kiritildi.")

                return JsonResponse({"message": "Muvaffaqiyatli tizimga kirdingiz."}, status=200)

            print("Xatolik: Login yoki parol noto'g'ri.")
            return JsonResponse({"error": "Login yoki parol noto'g'ri."}, status=401)

        except json.JSONDecodeError:
            print("Xatolik: JSON ma'lumotlari noto'g'ri.")
            return JsonResponse({"error": "Noto'g'ri so'rov ma'lumotlari."}, status=400)

        except Exception as e:
            print(f"Ichki xatolik yuz berdi: {str(e)}")
            return JsonResponse({"error": f"Ichki xatolik yuz berdi: {str(e)}"}, status=500)
