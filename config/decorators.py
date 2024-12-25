from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest


def verified_required(view_func):
    """
    Custom decorator to ensure:
    - Superusers are always allowed access.
    - Regular users must have `is_verified=True` to access.
    """
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Admin URL'larini chetlab o'tish
        if request.path.startswith("/admin/"):
            return view_func(request, *args, **kwargs)

        # Faqat oddiy foydalanuvchilar uchun tekshiruv
        if not request.user.is_superuser:
            if not getattr(request.user, 'is_verified', False):  # Tasdiqlanganligini tekshirish
                # Tasdiqlanmagan foydalanuvchi uchun yo'naltirish
                return redirect('waiting')  # Waiting sahifasi URL'iga yo'naltirish
        return view_func(request, *args, **kwargs)

    return _wrapped_view

def AddUserVerified(view_func):
    """
    Foydalanuvchi now_role bo'yicha cheklov kirituvchi dekorator.
    Faqat now_role=4, 5 yoki 6 bo'lgan foydalanuvchilarni kiritadi.
    """
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        allowed_roles = ['5', '6']  # Ruxsat berilgan rollar

        # Agar foydalanuvchi now_role ruxsat etilgan rollar ichida bo'lmasa
        if str(getattr(request.user, 'now_role', '')) not in allowed_roles:
            return redirect('validate-add-user')  # Tasdiqlash sahifasiga yo'naltirish

        return view_func(request, *args, **kwargs)

    return _wrapped_view
