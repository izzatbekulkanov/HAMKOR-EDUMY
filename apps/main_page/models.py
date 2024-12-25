from django.db import models

class SiteInfo(models.Model):
    SITE_TYPES = [
        ('ecommerce', 'E-Commerce'),
        ('blog', 'Blog'),
        ('portfolio', 'Portfolio'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255, verbose_name="Sayt nomi")
    admin_name = models.CharField(max_length=255, verbose_name="Administrator nomi")
    site_type = models.CharField(max_length=50, choices=SITE_TYPES, verbose_name="Sayt turi")
    is_active = models.BooleanField(default=True, verbose_name="Faol holati")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    def __str__(self):
        return f"{self.name} - {self.site_type} ({'Active' if self.is_active else 'Inactive'})"


class Season(models.Model):
    SEASON_NAMES = [
        ('spring', 'Bahor'),
        ('summer', 'Yoz'),
        ('autumn', 'Kuz'),
        ('winter', 'Qish'),
        ('space', 'Bosh'),
    ]

    name = models.CharField(max_length=50, choices=SEASON_NAMES, verbose_name="Fasl nomi")
    css_code = models.TextField(blank=True, verbose_name="CSS Kod")
    js_code = models.TextField(blank=True, verbose_name="JavaScript Kod")
    additional_info = models.TextField(blank=True, verbose_name="Qo'shimcha ma'lumotlar")
    is_active = models.BooleanField(default=False, verbose_name="Faol holati")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    def __str__(self):
        return f"{self.get_name_display()} ({'Active' if self.is_active else 'Inactive'})"
