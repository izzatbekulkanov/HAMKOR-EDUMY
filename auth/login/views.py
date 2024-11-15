from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from account.models import UserActivity
from auth.views import AuthView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class LoginView(AuthView):
    def get(self, request):
        if request.user.is_authenticated:
            # If the user is already logged in, redirect them to the home page or another appropriate page.
            return redirect("index")  # Replace 'index' with the actual URL name for the home page

        # Render the login page for users who are not logged in.
        return super().get(request)


CustomUser = get_user_model()  # CustomUser modelini olish


class JWTAuthView(APIView):
    permission_classes = [AllowAny]  # Kirish vaqtida autentifikatsiya talab qilinmaydi

    def post(self, request):
        username = request.data.get("email")  # Kirish uchun email yoki username maydonini olamiz
        password = request.data.get("password")

        # Foydalanuvchini autentifikatsiya qilish
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Django sessiyasi bilan tizimga kirish
            login(request, user)

            # UserActivity modelida log yaratish
            UserActivity.objects.create(
                user=user,
                login_time=timezone.now()  # Kirish vaqtini hozirgi vaqt bilan belgilash
            )

            # JWT tokenlarni yaratish
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # JWT tokenni va sessiya cookie'sini o'rnatish
            response = Response({"message": "Successfully logged in"}, status=status.HTTP_200_OK)
            response.set_cookie(
                key="access_token",
                value=str(access_token),
                httponly=True,
                secure=settings.DEBUG is False,  # Xavfsizlik uchun prodaksiyada True qilib qo'yish
                samesite="Lax",
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
            )

            # Refresh tokenni ham alohida cookie’da saqlash
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=settings.DEBUG is False,
                samesite="Lax",
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
            )
            return response
        else:
            return Response({"error": "Login yoki parol noto'g'ri"}, status=status.HTTP_401_UNAUTHORIZED)


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Cookie'dan access tokenni olish
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None  # Token yo'q bo'lsa, autentifikatsiya qilinmaydi
        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except AuthenticationFailed:
            return None  # Token noto'g'ri bo'lsa, autentifikatsiya qilinmaydi
