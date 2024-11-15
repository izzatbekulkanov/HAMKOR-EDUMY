from django.db import models
from django.contrib.auth import get_user_model
from account.models import CustomUser

# Django 3.1 va undan yuqori versiyalarga mos keladigan JSONField
try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField  # Django versiyasi past bo'lsa

class Center(models.Model):
    nomi = models.CharField(max_length=255, null=True, blank=True)
    rahbari = models.ForeignKey(CustomUser, on_delete=models.CASCADE, max_length=100, null=True, blank=True)

    def __str__(self):
        return self.nomi


User = get_user_model()

class Images(models.Model):
    image = models.ImageField(upload_to='center_images/', verbose_name="Rasm")
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    description = models.TextField(verbose_name="Tavsif", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Foydalanuvchi")

    def __str__(self):
        return self.title


class Filial(models.Model):
    center = models.ForeignKey('Center', on_delete=models.CASCADE, null=True, blank=True, verbose_name="O'quv markazi")
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="Joylashuv")
    contact = models.CharField(max_length=100, null=True, blank=True, verbose_name="Aloqa")
    telegram = models.CharField(max_length=100, null=True, blank=True, verbose_name="Telegram")
    image = models.ImageField(upload_to='filial_images/', null=True, blank=True, verbose_name="Bosh rasm")
    images = models.ManyToManyField(Images, blank=True, verbose_name="Qo'shimcha rasmlar")

    def __str__(self):
        return self.location


class Kasb(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="Yo'nalish nomi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")

    def __str__(self):
        return self.nomi


class Yonalish(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="Yo'nalish")
    kasb = models.ForeignKey(Kasb, on_delete=models.CASCADE, related_name='yonalishlar', verbose_name="Kasb")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")

    def __str__(self):
        return self.nomi


class Kurs(models.Model):
    yonalish = models.ForeignKey(Yonalish, on_delete=models.CASCADE, related_name='kurslar', verbose_name="Yo'nalish")
    nomi = models.CharField(max_length=255, verbose_name="Kurs nomi")
    narxi = models.BigIntegerField(verbose_name="Narxi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")

    def __str__(self):
        return f"{self.nomi} - {self.narxi}"


class E_groups(models.Model):
    DAYS_OF_WEEK = (
        ("Monday", "Dushanba"),
        ("Tuesday", "Seshanba"),
        ("Wednesday", "Chorshanba"),
        ("Thursday", "Payshanba"),
        ("Friday", "Juma"),
        ("Saturday", "Shanba"),
        ("Sunday", "Yakshanba"),
    )

    group_name = models.CharField(max_length=255, verbose_name="Guruh nomi")
    kurs = models.ForeignKey('center.Kurs', on_delete=models.CASCADE, related_name='groups', verbose_name="Kurs")
    days_of_week = JSONField(verbose_name="Dars kunlari", help_text="Hafta kunlarini tanlang", default=list, blank=True)

    students = models.ManyToManyField(CustomUser, through='GroupMembership', related_name='student_groups', verbose_name="O'quvchilar")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")

    def __str__(self):
        return f"{self.group_name} - {self.kurs.nomi}"

    def get_days_of_week_display(self):
        return ", ".join([dict(self.DAYS_OF_WEEK).get(day, day) for day in self.days_of_week])


class GroupMembership(models.Model):
    group = models.ForeignKey(E_groups, on_delete=models.CASCADE, verbose_name="Guruh")
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="O'quvchi")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")

    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Guruhga qo'shilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")

    def __str__(self):
        return f"{self.student} - {self.group.group_name} - {'Faol' if self.is_active else 'Nofaol'}"
