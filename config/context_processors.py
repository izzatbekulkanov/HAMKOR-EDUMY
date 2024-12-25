from django.conf import settings

from apps.main_page.models import Season


def my_setting(request):
    return {'MY_SETTING': settings}

def language_code(request):
    return {"LANGUAGE_CODE": request.LANGUAGE_CODE}

def get_cookie(request):
    return {"COOKIES": request.COOKIES}

# Add the 'ENVIRONMENT' setting to the template context
def environment(request):
    return {'ENVIRONMENT': settings.ENVIRONMENT}

# Add active season CSS to the template context
def active_season_css(request):
    active_season = Season.objects.filter(is_active=True).first()
    return {"ACTIVE_SEASON_CSS": active_season.css_code if active_season else ""}

# Add active season name to the template context
def active_season_name(request):
    active_season = Season.objects.filter(is_active=True).first()
    return {"ACTIVE_SEASON_NAME": active_season.name if active_season else ""}


def active_season_js(request):
    """
    Retrieve JavaScript code of the active season.
    """
    active_season = Season.objects.filter(is_active=True).first()
    return {"ACTIVE_SEASON_JS": active_season.js_code if active_season else ""}
