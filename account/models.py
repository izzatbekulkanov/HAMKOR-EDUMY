from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static

from school.models import Maktab


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
        """Superuserni yaratish uchun qo'shimcha ma'lumotlarni so'raydi."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser uchun is_staff=True bo‘lishi kerak.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser uchun is_superuser=True bo‘lishi kerak.')

        # Foydalanuvchi yaratishdan oldin user_type ni "6" (SuperAdmin) qilib o'rnatamiz
        extra_fields.setdefault('user_type', '6')

        # Qo'shimcha maydonlarni foydalanuvchidan so'rash
        first_name = input("Iltimos, ismni kiriting: ")
        second_name = input("Iltimos, familiyani kiriting: ")
        now_role = input("Hozirgi roli (default: '6'): ") or "6"

        extra_fields.update({
            'first_name': first_name,
            'second_name': second_name,
            'now_role': now_role,
        })

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
        ("6", "SuperAdmin"),
    )
    first_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Ism")
    second_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Familia")
    third_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Otasining ismi")

    p_first_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Ota onasining ismi")
    p_second_name = models.CharField(null=True, blank=True, max_length=255, verbose_name="Ota onasining familiya")
    p_phone_number = models.CharField(null=True, max_length=15, blank=True, verbose_name="Ota onasining telefon raqami")

    gender = models.ForeignKey('Gender', on_delete=models.SET_NULL, verbose_name="Jins", blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True, verbose_name="Tug'ilgan kun")
    imageFile = models.ImageField(upload_to='students/%Y/%m/%d', default=static('default/user.png'), verbose_name="Rasmi faylda", blank=True, null=True)

    regions = models.ForeignKey('Regions', on_delete=models.SET_NULL, verbose_name="Viloyat", null=True, blank=True)
    district = models.ForeignKey('District', on_delete=models.SET_NULL, verbose_name="Tuman", null=True, blank=True)
    quarters = models.ForeignKey('Quarters', on_delete=models.SET_NULL, verbose_name="Mahalla", blank=True, null=True)
    address = models.TextField(null=True, blank=True, verbose_name="Manzili")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="So'nggi kirish vaqti")
    last_logout = models.DateTimeField(null=True, blank=True, verbose_name="So'nggi chiqish vaqti")

    username = models.CharField(null=True, blank=True, max_length=255, unique=True)
    email = models.EmailField(null=True, blank=True, unique=True, verbose_name="Elektron pochta")

    phone_number = models.CharField(null=True, max_length=15, blank=True)
    password_save = models.CharField(_('password save'), max_length=128, blank=True, null=True)

    user_type = models.CharField(_('Type'), choices=type_choice, default="1", max_length=20, blank=True, null=True)

    roles = models.ManyToManyField('Roles', blank=True, verbose_name="Roles")
    now_role = models.CharField(null=True, blank=True, max_length=255, verbose_name="Foydalanuvchining hozirgi vaqtdagi roli", default="6")

    is_active = models.BooleanField(default=True)

    passport_serial = models.CharField(max_length=20, null=True, blank=True)
    passport_jshshir = models.CharField(max_length=20, null=True, blank=True)

    telegram = models.URLField(null=True, blank=True, verbose_name="Telegram profil havolasi")
    instagram = models.URLField(null=True, blank=True, verbose_name="Instagram profil havolasi")
    facebook = models.URLField(null=True, blank=True, verbose_name="Facebook profil havolasi")

    cashback = models.ManyToManyField('CashbackRecord', blank=True, verbose_name="Cashback turlari")
    e_groups = models.ManyToManyField('center.E_groups', blank=True, verbose_name="Kurslar")

    is_verified = models.BooleanField(default=False, verbose_name="Tasdiqlangan")

    maktab = models.ForeignKey('school.Maktab', on_delete=models.SET_NULL, verbose_name="Maktab", null=True, blank=True)
    sinf = models.ForeignKey('school.Sinf', on_delete=models.SET_NULL, verbose_name="Sinf", null=True, blank=True)

    added_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,related_name='created_users',verbose_name="Qo'shgan foydalanuvchi")
    def __str__(self):
        return self.username or self.phone_number or self.first_name

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Users log in with their email
    REQUIRED_FIELDS = ['username']

    @property
    def total_cashback_sum(self):
        """
        Jami cashback summasini hisoblash.
        """
        return self.cashback.aggregate(total_sum=models.Sum('cashback__summasi'))['total_sum'] or 0

    @property
    def paid_cashback_sum(self):
        """
        To'langan cashback summasini hisoblash.
        """
        return self.cashback.filter(is_paid=True).aggregate(total_sum=models.Sum('cashback__summasi'))['total_sum'] or 0






class Cashback(models.Model):
    type_choices = (
        ("1", "Ro'yhatdan o'tganlik uchun"),
        ("2", "Qabul qilingani"),
        ("3", "Kurs uchun to'lov"),
        ("4", "Referal tizim"),
        ("5", "Direktor uchun"),
        ("6", "Guruhga qo'shilish"),  # Yangi tanlov
    )

    User = get_user_model()  # Foydalanuvchi modelini olish
    user_type_choices = User.type_choice  # Foydalanuvchi turlari uchun choices

    name = models.CharField(max_length=255, verbose_name="Cashback turi")
    summasi = models.BigIntegerField(verbose_name="Cashback summa", default=0)
    parent_summ = models.BigIntegerField(verbose_name="Parent uchun summa", default=0)
    type = models.CharField(max_length=20, choices=type_choices, verbose_name="Turi", null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=user_type_choices, verbose_name="Foydalanuvchi turi")
    submitted_student = models.ForeignKey(
        'center.SubmittedStudent', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="SubmittedStudent"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    center = models.ForeignKey('center.Center', on_delete=models.CASCADE, null=True, blank=True, verbose_name="O'quv markazi")

    @staticmethod
    def get_filtered_user_type_choices():
        """
        CustomUser.type_choice dan faqat ruxsat etilgan turlarni olish uchun.
        """
        User = get_user_model()
        return [choice for choice in User.type_choice if choice[0] not in ["4", "5"]]

    @property
    def filtered_user_type_choices(self):
        """
        Foydalanuvchi turlarini olish uchun property sifatida foydalaniladi.
        """
        return self.get_filtered_user_type_choices()

    def __str__(self):
        return self.name

class CashbackRecord(models.Model):
    cashback = models.ForeignKey(Cashback, on_delete=models.CASCADE, verbose_name="Asosiy Cashback")
    teacher = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, verbose_name="O'qituvchi")
    student = models.ForeignKey('center.SubmittedStudent', on_delete=models.CASCADE, verbose_name="O'quvchi")
    is_viewed = models.BooleanField(default=False, verbose_name="Ko'rilganmi")
    is_paid = models.BooleanField(default=False, verbose_name="To'langanmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")  # Yangilandi

    def __str__(self):
        return f"{self.cashback.name} - {self.teacher.first_name} {self.teacher.second_name} uchun"

class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="activities", verbose_name="Foydalanuvchi")
    login_time = models.DateTimeField(default=timezone.now, verbose_name="Kirish vaqti")
    logout_time = models.DateTimeField(null=True, blank=True, verbose_name="Chiqish vaqti")

    def __str__(self):
        return f"{self.user.username} - Kirish: {self.login_time}, Chiqish: {self.logout_time}"
