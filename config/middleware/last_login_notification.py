from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now

class LastLoginNotificationMiddleware:
    """
    Middleware foydalanuvchining tizimga oxirgi kirish vaqtini sessiyaga yozadi va bildirishnoma ko'rsatadi.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            if 'show_login_toastr' not in request.session:
                # Sessiyaga qiymatlarni yozish
                last_login = request.user.last_login
                if last_login:
                    request.session['last_login'] = last_login.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    request.session['last_login'] = 'Bu foydalanuvchining birinchi kirishi'

                # Toastrni ko'rsatish uchun flag qo'shish
                request.session['show_login_toastr'] = True

            # Foydalanuvchining oxirgi kirish vaqtini yangilash
            request.user.last_login = now()
            request.user.save()

        response = self.get_response(request)
        return response
