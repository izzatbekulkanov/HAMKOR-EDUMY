from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def verified_required(view_func):
    """
    Custom decorator to ensure:
    - Superusers are always allowed access.
    - Regular users must have `is_verified=True` to access.
    """
    @login_required
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:  # Faqat oddiy foydalanuvchilar uchun tasdiqlashni tekshirish
            if not request.user.is_verified:  # Tasdiqlanganligini tekshirish
                # Agar foydalanuvchi tasdiqlanmagan bo'lsa, "waiting" sahifasiga yo'naltirish
                return redirect('waiting')  # 'waiting' ni haqiqiy URL nomiga mos ravishda almashtiring
        # Superuser yoki tasdiqlangan foydalanuvchi bo'lsa, ruxsat berish
        return view_func(request, *args, **kwargs)

    return _wrapped_view
