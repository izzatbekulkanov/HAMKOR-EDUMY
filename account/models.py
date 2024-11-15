from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """CustomUser model uchun username maydonisiz model menejerini aniqlash."""

    def _create_user(self, email, password=None, **extra_fields):
        """Berilgan email va parol bilan CustomUser yaratib saqlash."""
        if not email:
            raise ValueError('Berilgan email majburiy')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Berilgan email va parol bilan SuperUser yaratib saqlash."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff=True bo‘lishi kerak.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser=True bo‘lishi kerak.')

        return self._create_user(email, password, **extra_fields)


class Gender(models.Model):
    code = models.CharField(max_length=20, verbose_name="Jins kodi")
    name = models.CharField(max_length=255, verbose_name="Jins nomi")

    def __str__(self):
        return self.name


class Regions(models.Model):
    code = models.CharField(max_length=20, verbose_name="Viloyat kodi")
    name = models.CharField(max_length=255, verbose_name="Viloyat nomi")

    def __str__(self):
        return self.name


class District(models.Model):
    code = models.CharField(max_length=20, verbose_name="Tuman kodi")
    region = models.ForeignKey(Regions, on_delete=models.CASCADE, verbose_name="Viloyat kodi")
    name = models.CharField(max_length=255, verbose_name="Tuman nomi")

    def __str__(self):
        return self.name


class Quarters(models.Model):
    code = models.CharField(max_length=20, verbose_name="Mahalla kodi")
    district = models.ForeignKey(District, on_delete=models.CASCADE, verbose_name="Tuman kodi")
    name = models.CharField(max_length=255, verbose_name="Mahalla nomi")

    def __str__(self):
        return self.name


class Roles(models.Model):
    code = models.CharField(max_length=20, verbose_name="role kodi")
    name = models.CharField(max_length=255, verbose_name="role nomi")

    def __str__(self):
        return self.name





class CustomUser(AbstractUser):
    type_choice = (
        ("1", "O'quvchi"),
        ("2", "O'qituvchi"),
        ("3", "Direktor"),
        ("4", "Administrator"),
        ("5", "CEO_Administrator"),
    )
    first_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Ism")
    second_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Familia")
    third_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Otasining ismi")

    p_first_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Ota onasining ismi")
    p_second_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Ota onasining familiya")
    p_phone_number = models.CharField(null=True, max_length=15, blank=True, verbose_name="Ota onasining telefon raqami")

    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, verbose_name="Jins", blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True, verbose_name="Tug'ilgan kun")
    imageFile = models.ImageField(upload_to='students/%Y/%m/%d', default='default/user.png', verbose_name="Rasmi faylda", blank=True, null=True)

    regions = models.ForeignKey(Regions, on_delete=models.SET_NULL, verbose_name="Viloyat", null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, verbose_name="Tuman", null=True, blank=True)
    quarters = models.ForeignKey(Quarters, on_delete=models.SET_NULL, verbose_name="Mahalla", blank=True, null=True)
    address = models.TextField(null=True, blank=True, verbose_name="Manzili")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="So'nggi kirish vaqti")
    last_logout = models.DateTimeField(null=True, blank=True, verbose_name="So'nggi chiqish vaqti")


    username = models.CharField(null=True, blank=True, max_length=255, unique=True)
    email = models.CharField(null=True, blank=True, max_length=255, unique=True)

    phone_number = models.CharField(null=True, max_length=15, blank=True)
    password_save = models.CharField(('password save'), max_length=128, blank=True, null=True)  # Added password_save field

    user_type = models.CharField(_('Type'), choices=type_choice, default="1", max_length=20, blank=True, null=True)

    roles = models.ManyToManyField(Roles, blank=True, verbose_name="Roles")  # Allows multiple roles per user
    now_role = models.CharField(null=True, blank=True, max_length=255, verbose_name="Foydalanuvchining hozirgi vaqtdagi roli")

    is_active = models.BooleanField(default=True)

    passport_serial = models.CharField(max_length=20, null=True, blank=True)
    passport_jshshir = models.CharField(max_length=20, null=True, blank=True)

    telegram = models.URLField(null=True, blank=True, verbose_name="Telegram profil havolasi")
    instagram = models.URLField(null=True, blank=True, verbose_name="Instagram profil havolasi")
    facebook = models.URLField(null=True, blank=True, verbose_name="Facebook profil havolasi")

    cashback = models.ManyToManyField('Cashback', blank=True, verbose_name="Cashback turlari")
    e_groups = models.ManyToManyField('center.E_groups', blank=True, verbose_name="Kurslar")

    def __str__(self):
        return self.username or self.email or self.first_name

    USERNAME_FIELD = 'email'  # Users log in with their email
    REQUIRED_FIELDS = ['username']  # username required field

class Cashback(models.Model):
    type_choices = (
        ("1", "Referal tizim"),
        ("2", "Kurs uchun to'lov"),
        ("3", "Admin"),
        # Additional types if necessary
    )

    # Filtered type_choice for user_type, excluding "Administrator" and "CEO_Administrator"
    filtered_user_type_choices = [choice for choice in CustomUser.type_choice if choice[0] not in ["4", "5"]]

    name = models.CharField(max_length=255, verbose_name="Cashback turi")
    summasi = models.BigIntegerField(verbose_name="Cashback summa", default=0)
    type = models.CharField(max_length=20, choices=type_choices, verbose_name="Turi", null=True, blank=True)
    user_type = models.CharField(
        max_length=20,
        choices=filtered_user_type_choices,
        verbose_name="Foydalanuvchi turi"
    )  # New field with filtered user type choices
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")

    def __str__(self):
        return self.name


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="activities", verbose_name="Foydalanuvchi")
    login_time = models.DateTimeField(default=timezone.now, verbose_name="Kirish vaqti")
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name="Chiqish vaqti")

    def __str__(self):
        return f"{self.user.username} - Kirish: {self.login_time}, Chiqish: {self.logout_time}"
