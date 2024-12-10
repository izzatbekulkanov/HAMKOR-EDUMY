from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'custom_login.html'
    redirect_authenticated_user = True
    next_page = '/admin/'

    def get_context_data(self, **kwargs):
        # Importni kerakli joyda bajaring
        from auth.views import AuthView
        context = super().get_context_data(**kwargs)
        return context
