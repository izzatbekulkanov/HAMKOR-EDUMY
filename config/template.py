# Shablon sozlamalari
# ------------------------------------------------------------------------------

# Shablon tartibi shablonlari katalogi

# Shablon sozlamalari
# ? Shablon sozlamalarini bu yerdan osongina o'zgartiring
# ? Shablon sozlamalarini demo konfiguratsiyalar bilan o'zgartirish uchun ushbu ob'ektni template-config/demo-*.py faylidagi TEMPLATE_CONFIG bilan almashtiring
TEMPLATE_CONFIG = {
    "layout": "horizontal",             # Variantlar[String]: vertical(standart), horizontal
    "theme": "theme-default",         # Variantlar[String]: theme-default(standart), theme-bordered, theme-semi-dark
    "style": "light",                 # Variantlar[String]: light(standart), dark, tizim rejimi
    "rtl_support": True,              # Variantlar[Boolean]: True(standart), False # O'ngdan chapga (RTL) qo'llab-quvvatlash berilishi yoki berilmasligi
    "rtl_mode": False,                # Variantlar[Boolean]: False(standart), True # Tartibni RTL tartibiga o'rnatish (rtl_mode uchun rtl_support True bo'lishi kerak)
    "has_customizer": True,           # Variantlar[Boolean]: True(standart), False # Sozlash panelini ko'rsatish yoki ko'rsatmaslik. BUNI O‘ZGARTIRISHDA QO‘SHILGAN JS FAYLI O‘CHIRILADI. SHU SABABLI, LOCAL STORAGE ISHLAMAYDI
    "display_customizer": True,       # Variantlar[Boolean]: True(standart), False # Sozlash interfeysini ko'rsatish yoki ko'rsatmaslik. BUNI O‘ZGARTIRISHDA QO‘SHILGAN JS FAYLI O‘CHIRILMAYDI. SHU SABABLI, LOCAL STORAGE ISHLAYDI
    "content_layout": "wide",         # Variantlar[String]: 'compact', 'wide' (compact=container-xxl, wide=container-fluid)
    "navbar_type": "fixed",           # Variantlar[String]: 'fixed', 'static', 'hidden' (Faqat vertikal tartib uchun)
    "header_type": "fixed",           # Variantlar[String]: 'static', 'fixed' (Faqat gorizontal tartib uchun)
    "menu_fixed": True,               # Variantlar[Boolean]: True(standart), False # Menyu (Layout) mahkamlangan (Faqat vertikal tartib uchun)
    "menu_collapsed": False,          # Variantlar[Boolean]: False(standart), True # Menyu qisqartirilgan holda ko'rsatish, Faqat vertikal tartib uchun
    "footer_fixed": False,            # Variantlar[Boolean]: False(standart), True # Pastki qism (footer) mahkamlangan
    "show_dropdown_onhover": True,    # True, False (Faqat gorizontal tartib uchun)
    "customizer_controls": [
        "rtl",
        "style",
        "headerType",
        "contentLayout",
        "layoutCollapsed",
        "showDropdownOnHover",
        "layoutNavbarOptions",
        "themes",
    ],  # Sozlash opsiyalarini ko'rsatish/yashirish uchun
}


# Theme Variables
# ? Personalize template by changing theme variables (For ex: Name, URL Version etc...)
THEME_VARIABLES = {
    "creator_name": "PixInvent",
    "creator_url": "https://pixinvent.com/",
    "template_name": "English House",
    "template_suffix": "Django Admin Template",
    "template_version": "2.0.0",
    "template_free": False,
    "template_description": "EDUMY is a modern, clean and fully responsive admin template built with Bootstrap 5, Django, HTML, CSS, jQuery, and JavaScript. It has a huge collection of reusable UI components and integrated with the latest jQuery plugins. It can be used for all types of web applications like custom admin panel, project management system, admin dashboard, Backend application or CRM.",
    "template_keyword": "django, django admin, dashboard, bootstrap 5 dashboard, bootstrap 5 design, bootstrap 5",
    "facebook_url": "https://www.facebook.com/pixinvents/",
    "twitter_url": "https://twitter.com/pixinvents",
    "github_url": "https://github.com/pixinvent",
    "dribbble_url": "https://dribbble.com/pixinvent",
    "instagram_url": "https://www.instagram.com/pixinvents/",
    "license_url": "https://themeforest.net/licenses/standard",
    "live_preview": "https://demos.pixinvent.com/vuexy-html-django-admin-template/demo-1/",
    "product_page": "https://1.envato.market/vuexy_admin",
    "support": "https://pixinvent.ticksy.com/",
    "more_themes": "https://1.envato.market/pixinvent_portfolio",
    "documentation": "https://demos.pixinvent.com/vuexy-html-admin-template/documentation/django-introduction.html",
    "changelog": "https://demos.pixinvent.com/vuexy/changelog.html",
    "git_repository": "EDUMY-html-django-admin-template",
    "git_repo_access": "https://tools.pixinvent.com/github/github-access",
}


# ! Don't change THEME_LAYOUT_DIR unless it's required
THEME_LAYOUT_DIR = "layout"
