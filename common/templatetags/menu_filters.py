# templatetags/menu_filters.py
from django import template

register = template.Library()

@register.filter
def filter_menu_by_role(menu_items, now_role):
    """
    Foydalanuvchi now_role asosida menyu elementlarini filtrlash.
    """
    filtered_menu = []
    for item in menu_items:
        # Agar menyu elementida "allowed_roles" bo'lsa, filtrlang
        if "allowed_roles" in item:
            if now_role in item["allowed_roles"]:
                filtered_menu.append(item)
        else:
            # Agar "allowed_roles" bo'lmasa, menyuni qo'sh
            filtered_menu.append(item)
    return filtered_menu
