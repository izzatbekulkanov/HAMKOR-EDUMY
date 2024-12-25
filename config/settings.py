import os
from pathlib import Path
from datetime import timedelta
from django.utils.translation import gettext_lazy as _
from decouple import config
from .template import TEMPLATE_CONFIG, THEME_LAYOUT_DIR, THEME_VARIABLES




BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='fallback-secret-key')

# DEBUG = config('DEBUG', default=False, cast=bool)

DEBUG = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "ref.edumy.uz", "inihub.namspi.uz"]

ENVIRONMENT = config('DJANGO_ENVIRONMENT', default='local')

os.environ.get
LOCAL_APPS = [
    "account",
    "center",
    "school",
    "api",
    'auth.apps.AuthConfig',
    "common"
]

IN_APPS = [
    "apps.landing_page",
    "apps.main_page",
    "apps.settings_page",
    "apps.user_page"
]

GLOBAL_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
]

SYSTEM_APPS = [
    'jazzmin',
    "django.contrib.admin",
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

]


INSTALLED_APPS = SYSTEM_APPS + LOCAL_APPS + GLOBAL_APPS + IN_APPS

AUTH_USER_MODEL = 'account.CustomUser'

# settings.py
AUTHENTICATION_BACKENDS = [
    'auth.custom_backend.CustomBackend',  # CustomBackend'ning yo'li
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,  # refresh tokenni avtomatik ravishda yangilash
    'BLACKLIST_AFTER_ROTATION': True,  # refresh token yangilanganda eski tokenni qora ro'yxatga qo'shish
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'ALGORITHM': 'HS256',  # Asosiy xavfsizlik algoritmi
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'TOKEN_TYPE_CLAIM': 'token_type',
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "web_project.language_middleware.DefaultLanguageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
MIDDLEWARE += [
    "config.middleware.last_login_notification.LastLoginNotificationMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.language_code",
                "config.context_processors.my_setting",
                "config.context_processors.get_cookie",
                "config.context_processors.environment",
                "config.context_processors.active_season_css",
                "config.context_processors.active_season_js",
            ],
            "libraries": {
                "theme": "web_project.template_tags.theme",
            },
            "builtins": [
                "django.templatetags.static",
                "web_project.template_tags.theme",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
    ("ar", _("Arabic")),
    ("de", _("German")),
]

TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

SITE_ID = 1

LOCALE_PATHS = [BASE_DIR / "locale"]


# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Productionda collectstatic ishlashi uchun STATICFILES_DIRS ni to'g'ri sozlang
STATICFILES_DIRS = [
    BASE_DIR / "src" / "assets",  # Qo'shimcha statik fayllar joylashuvi
]


# # Statik va media fayllar konfiguratsiyasi
# if ENVIRONMENT == "production":
#     # Ishlab chiqarish muhitida
#     STATIC_URL = "/static/"
#     STATIC_ROOT = BASE_DIR / "staticfiles"  # `collectstatic` bilan fayllarni shu joyga yig'adi
#     MEDIA_URL = '/media/'
#     MEDIA_ROOT = BASE_DIR / 'media'
# else:
#     # Lokal muhitda
#     STATIC_URL = "/static/"
#     STATICFILES_DIRS = [BASE_DIR / "src" / "assets"]
#     MEDIA_URL = '/media/'
#     MEDIA_ROOT = BASE_DIR / 'media'

# # Statik va media fayllar konfiguratsiyasi
# STATIC_URL = "/static/"

# if ENVIRONMENT == "production":
#     # Ishlab chiqarish muhitida
#     STATIC_ROOT = BASE_DIR / "staticfiles"
# else:
#     # Lokal muhitda collectstatic ishlatilmasdan
#     STATICFILES_DIRS = [BASE_DIR / "src" / "assets"]

# Media fayllar uchun sozlamalar
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


#
# BASE_URL = os.environ.get("BASE_URL", default="https://ref.edumy.uz")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

THEME_LAYOUT_DIR = THEME_LAYOUT_DIR
TEMPLATE_CONFIG = TEMPLATE_CONFIG
THEME_VARIABLES = THEME_VARIABLES

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""

LOGIN_URL = "/login/"
LOGOUT_REDIRECT_URL = "/"

SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 3600  # 20 minutes
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

SESSION_COOKIE_AGE = 3600

SECURE_HSTS_SECONDS = 31536000  # HSTPSTS (HT Strict Transport Security) faollashtirish
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # Subdomenlarga ham HSTS
SECURE_HSTS_PRELOAD = True  # HSTS preload ro'yxatiga qo'shish
SECURE_CONTENT_TYPE_NOSNIFF = True  # Xavfsizlik uchun MIME turi tekshiruvi
SECURE_BROWSER_XSS_FILTER = True  # XSS hujumlariga qarshi himoya


CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://ref.edumy.uz",
    "https://inihub.namspi.uz",
    "https://www.ref.edumy.uz",
]



JAZZMIN_SETTINGS = {
    # Title and Branding
    "site_title": "Hamkor Edumy Admin",
    "site_header": "Hamkor Edumy",
    "site_brand": "Hamkor Edumy",
    "site_logo": "img/branding/logo.png",
    "site_icon": "img/hamkor/img/favicon.ico",
    "welcome_sign": "Xush kelibsiz! Hamkor Edumy tizimiga kirish",
    "copyright": "© 2024 Izzatbek Ulkanov",

    ####################
    # Login Page Setup #
    ####################
    "login_logo": "img/branding/logo.png",  # Kirish oynasi uchun logotip
    "login_logo_dark": "img/branding/logo.png",  # Qorong'u mavzuda ishlatiladigan logotip
    "login_background": "img/branding/login-bg.jpg",  # Kirish oynasi uchun fon rasmi
    "user_avatar": "img/users/default-avatar.png",  # Foydalanuvchi uchun avatar rasmi


    ################
    # Sidebar Setup #
    ################
    "show_sidebar": True,
    "navigation_expanded": False,  # Default: Auto-expand menus

    # Sidebar ordering
    "order_with_respect_to": [
        "auth",
        "account",
        "center",
        "school",
        "auth_token",
        "sites",
    ],

    #####################
    # Top Navigation Bar #
    #####################
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Contact", "url": "#", "new_window": True},
        {"model": "auth.User"},  # User Model topmenyuda qidirish uchun
    ],


    #####################
    # Sidebar Search #
    #####################
    "search_model": ["auth.User", "account.CustomUser", "auth.Group"],  # Sidebar qidiruv modeli



    #################
    # App Icons #
    #################
    "icons": {
        # Auth
        "auth": "fas fa-users-cog",
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",

        # Account
        "account": "fas fa-user",
        "account.Cashback": "fas fa-coins",
        "account.District": "fas fa-map-marker-alt",
        "account.Gender": "fas fa-venus-mars",
        "account.Quarters": "fas fa-th",
        "account.Regions": "fas fa-globe",
        "account.Roles": "fas fa-user-tag",
        "account.CustomUser": "fas fa-user-circle",
        "account.UserActivity": "fas fa-chart-line",

        # Center
        "center": "fas fa-building",
        "center.Center": "fas fa-building",
        "center.E_groups": "fas fa-users",
        "center.Filial": "fas fa-map",
        "center.Images": "fas fa-image",
        "center.Kasb": "fas fa-briefcase",
        "center.Kurs": "fas fa-graduation-cap",
        "center.SubmittedStudent": "fas fa-check-circle",
        "center.Yonalish": "fas fa-route",

        # School
        "school": "fas fa-school",
        "school.Belgisi": "fas fa-tag",
        "school.Maktab": "fas fa-building",
        "school.Sinf": "fas fa-chalkboard-teacher",

        # Sites
        "sites": "fas fa-sitemap",
        "sites.Site": "fas fa-line",
    },

    ######################
    # Notification Items #
    ######################
    "usermenu_links": [
        {"name": "Notifications", "url": "#", "icon": "fas fa-bell", "new_window": False},
        {"name": "Messages", "url": "#", "icon": "fas fa-envelope", "new_window": False},
        {"name": "Asosiy sahifa", "url": "/", "icon": "fas fa-cog", "new_window": False},  # `/` URL to‘g‘rilandi
        # {"name": "Logout", "url": "/logout/", "icon": "fas fa-sign-out-alt", "new_window": False},
    ],

    "custom_links": {
        "auth": [
            {"name": "Logout", "url": "/logout/", "icon": "fas fa-sign-out-alt", "new_window": False},
        ]
    },

    ##################
    # Night Mode #
    ##################
    "theme": {
        "default_mode": "dark",  # Default holatda qorong'u rejim
        "toggle_button": True,  # Kun-tun rejimi tugmasi
    },
    #################
    # UI Tweaks #
    #################
    "custom_css": "css/custom-adminlte.css",  # Add your custom CSS
    "custom_js": "js/custom-adminlte.js",  # Add your custom JS
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": True,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": True,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": True,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": True,
    "theme": "solar",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": True
}
