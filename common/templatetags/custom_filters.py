from django import template

register = template.Library()

@register.filter
def get_verbose_day(day):
    """
    Hafta kunlarini O'zbek tilida qaytaradi.
    """
    days_translation = {
        "Monday": "Dushanba",
        "Tuesday": "Seshanba",
        "Wednesday": "Chorshanba",
        "Thursday": "Payshanba",
        "Friday": "Juma",
        "Saturday": "Shanba",
        "Sunday": "Yakshanba",
    }
    return days_translation.get(day, day)


def format_phone_number(phone_number):
    """
    Telefon raqamni +998 (99) 999-99-99 formatida qaytaradi.
    """
    if not phone_number or len(phone_number) != 13 or not phone_number.startswith('+'):
        return phone_number  # Noto'g'ri raqam formatini qaytaradi

    return f"{phone_number[:4]} ({phone_number[4:6]}) {phone_number[6:9]}-{phone_number[9:11]}-{phone_number[11:]}"


@register.filter
def phone_format(value):
    """
    Telefon raqamni +998 (99) 999-99-99 formatida ko'rsatish uchun.
    """
    return format_phone_number(value)