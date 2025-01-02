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