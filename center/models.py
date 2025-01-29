from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from account.models import CustomUser
from django.utils.timezone import now
from school.models import Maktab, Sinf, Belgisi
from django.core.validators import RegexValidator

# Django 3.1 va undan yuqori versiyalarga mos keladigan JSONField
try:
    from django.db.models import JSONField, Sum
except ImportError:
    from django.contrib.postgres.fields import JSONField  # Django versiyasi past bo'lsa


class Center(models.Model):
    nomi = models.CharField(max_length=255, null=True, blank=True, verbose_name="Markaz nomi")
    rahbari = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, max_length=100, null=True, blank=True,
                                verbose_name="Rahbari")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    is_verified = models.BooleanField(default=False, verbose_name="Tasdiqlanganmi")
    all_views = models.BooleanField(default=False, verbose_name="Barchaga ko'rinadi")

    # Many-to-ManyField for schools
    maktab = models.ManyToManyField(
        "school.Maktab",
        blank=True,
        related_name="centers",
        verbose_name="Maktablar",
    )

    def __str__(self):
        return self.nomi or "Markaz"


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
    images = models.ManyToManyField('Images', blank=True, verbose_name="Qo'shimcha rasmlar")
    admins = models.ManyToManyField(CustomUser, blank=True, related_name="administered_filials", verbose_name="Administratorlar")  # Adminlar maydoni
    created_at = models.DateTimeField(default=now, verbose_name="Qo'shilgan vaqt")  # Qo'shilgan vaqt maydoni
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    def __str__(self):
        return self.location or "Filial"


class Kasb(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE, related_name='kasblar', verbose_name="Markaz")
    nomi = models.CharField(max_length=255, verbose_name="Kasb nomi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    added_by = models.ForeignKey(
        'account.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_kasblar',
        verbose_name="Qo'shgan foydalanuvchi"
    )

    def __str__(self):
        return self.nomi


class Yonalish(models.Model):
    kasb = models.ForeignKey(
        'Kasb', on_delete=models.SET_NULL, related_name='yonalishlar', verbose_name="Kasb", null=True, blank=True
    )
    center = models.ForeignKey(
        'Center', on_delete=models.CASCADE, related_name='yonalishlar', verbose_name="Markaz"
    )
    nomi = models.CharField(max_length=255, verbose_name="Yo'nalish nomi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    kurslar = models.ManyToManyField(
        'Kurs', related_name='yonalishlar', verbose_name="Kurslar", blank=True
    )

    def __str__(self):
        return self.nomi


class Kurs(models.Model):
    center = models.ForeignKey(
        'Center', on_delete=models.CASCADE, related_name='kurslar', verbose_name="Markaz"
    )
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
    kurs = models.ForeignKey(
        'center.Kurs',
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name="Kurs"
    )
    days_of_week = JSONField(
        verbose_name="Dars kunlari",
        help_text="Hafta kunlarini tanlang",
        default=list,
        blank=True
    )
    # Many-to-ManyField with through argument
    students = models.ManyToManyField(
        'center.SubmittedStudent',
        through='GroupMembership',  # Yangi GroupMembership modeli bilan bog'lanish
        related_name='student_groups',
        verbose_name="O'quvchilar"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    center = models.ForeignKey('Center', on_delete=models.CASCADE, related_name='guruhlar', verbose_name="Markaz", null=True, blank=True)

    def __str__(self):
        return f"{self.group_name} - {self.kurs.nomi}"

    def get_days_of_week_display(self):
        return ", ".join([dict(self.DAYS_OF_WEEK).get(day, day) for day in self.days_of_week])


class GroupMembership(models.Model):
    group = models.ForeignKey(
        "center.E_groups",  # Guruhni belgilash
        on_delete=models.CASCADE,
        verbose_name="Guruh"
    )
    student = models.ForeignKey(
        "center.SubmittedStudent",  # SubmittedStudent bilan bog'lash
        on_delete=models.CASCADE,
        verbose_name="O'quvchi"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Guruhga qo'shilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.group.group_name} - {'Faol' if self.is_active else 'Nofaol'}"


class SubmittedStudent(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('accepted', 'Qabul qilingan'),
        ('accept_group', 'Guruhga qabul qilindi'),
        ('rejected', 'Rad etilgan'),
        ('paid', 'To‘lov qilindi'),  # ✅ Yangi holat qo‘shildi
    ]

    # Shaxsiy ma'lumotlar
    first_name = models.CharField(max_length=100, verbose_name="Ismi")
    last_name = models.CharField(max_length=100, verbose_name="Familiyasi")
    phone_number = models.CharField(
        max_length=13,
        verbose_name="Telefon raqami",
        validators=[RegexValidator(
            regex=r'^\+998\d{9}$',
            message="Telefon raqami +998 bilan boshlanishi va 9 ta raqamdan iborat bo'lishi kerak."
        )]
    )

    # Bog‘langan modellar
    sinf = models.ForeignKey('school.Sinf', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sinf")
    kasb = models.ForeignKey('center.Kasb', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kasb")
    yonalish = models.ForeignKey('center.Yonalish', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Yo'nalish")
    filial = models.ForeignKey('center.Filial', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Filial")
    kurslar = models.ManyToManyField(
        'center.Kurs',
        blank=True,
        related_name='submitted_students',
        verbose_name="Kurslar"
    )

    belgisi = models.CharField(max_length=100, verbose_name="Sinf Belgisi")

    # Holat
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name="Holati")

    # Qo'shgan foydalanuvchi
    added_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Qo'shgan foydalanuvchi")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status}"

class StudentDetails(models.Model):
    student = models.OneToOneField(
        'SubmittedStudent',
        on_delete=models.CASCADE,
        related_name="details",
        verbose_name="O'quvchi"
    )
    # Shaxsiy ma'lumotlar
    birth_date = models.DateField(verbose_name="Tug'ilgan sana", blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Erkak'), ('female', 'Ayol')],
        verbose_name="Jinsi",
        blank=True,
        null=True
    )
    address = models.TextField(verbose_name="Manzili", blank=True, null=True)
    region = models.CharField(max_length=100, verbose_name="Viloyat", blank=True, null=True)
    district = models.CharField(max_length=100, verbose_name="Tuman", blank=True, null=True)

    # Ota-ona ma'lumotlari
    parent_name = models.CharField(max_length=200, verbose_name="Ota-onaning ismi", blank=True, null=True)
    parent_phone = models.CharField(
        max_length=13,
        verbose_name="Ota-onaning telefon raqami",
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+998\d{9}$',
            message="Telefon raqami +998 bilan boshlanishi va 9 ta raqamdan iborat bo'lishi kerak."
        )]
    )
    relationship_to_student = models.CharField(
        max_length=50,
        verbose_name="Ota-onaning o'quvchiga munosabati",
        blank=True,
        null=True
    )  # Masalan, "Ota", "Ona", "Bobo", va hokazo.

    # Qo'shimcha o'quv ma'lumotlari
    previous_school = models.CharField(max_length=200, verbose_name="Oldingi maktab", blank=True, null=True)
    medical_conditions = models.TextField(verbose_name="Tibbiy holatlar", blank=True, null=True)
    hobbies = models.TextField(verbose_name="Xobbilari", blank=True, null=True)

    # Ijtimoiy ma'lumotlar
    social_media_link = models.URLField(verbose_name="Ijtimoiy tarmoq havolasi", blank=True, null=True)
    photo = models.ImageField(
        upload_to='students/photos/',
        verbose_name="O'quvchining rasmi",
        blank=True,
        null=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    def __str__(self):
        return f"Qo'shimcha ma'lumot: {self.student.first_name} {self.student.last_name}"

    class Meta:
        verbose_name = "O'quvchining batafsil ma'lumotlari"
        verbose_name_plural = "O'quvchilarni batafsil ma'lumotlari"


class PaymentRecord(models.Model):
    student = models.ForeignKey(
        "center.SubmittedStudent", on_delete=models.CASCADE, verbose_name="O'quvchi"
    )
    group = models.ForeignKey(
        "center.E_groups", on_delete=models.CASCADE, verbose_name="Guruh"
    )
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="To'langan summa"
    )
    total_debt = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Umumiy qarzdorlik"
    )
    remaining_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Qoldiq qarz"
    )
    total_lessons_in_month = models.PositiveIntegerField(
        default=0, verbose_name="Butun oy ichidagi darslar soni"
    )
    attended_lessons = models.PositiveIntegerField(
        default=0, verbose_name="O'quvchi kelgan kundan boshlab darslar soni"
    )
    payment_date = models.DateField(
        auto_now_add=True, verbose_name="To'lov sanasi"
    )
    month = models.PositiveIntegerField(verbose_name="To'lov oyi")
    year = models.PositiveIntegerField(verbose_name="To'lov yili")
    course_total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Kursning umumiy narxi"
    )

    def __str__(self):
        return f"{self.student} - {self.group.group_name} uchun {self.amount_paid} so'm to'landi"

    @classmethod
    def calculate_payment(cls, student, group, start_date=None):
        """
        O‘quvchi guruhga kelgan sanadan boshlab, oy oxirigacha qancha dars borligini hisoblaydi.
        """
        if not start_date:
            start_date = now().date()

        # **Oyning oxirgi kunini olish**
        end_of_month = date(start_date.year, start_date.month, 1) + timedelta(days=32)
        end_of_month = date(end_of_month.year, end_of_month.month, 1) - timedelta(days=1)

        # **Guruhning dars kunlarini olish**
        lesson_days = group.days_of_week  # Masalan: ["Monday", "Wednesday", "Friday"]

        # **Jami oy ichidagi barcha dars kunlarini hisoblash**
        total_lessons_in_month = sum(
            1 for i in range((end_of_month - date(start_date.year, start_date.month, 1)).days + 1)
            if (date(start_date.year, start_date.month, 1) + timedelta(days=i)).strftime('%A') in lesson_days
        )

        # **O‘quvchi kelgan kundan boshlab, oy oxirigacha nechta dars borligini hisoblash**
        attended_lessons = sum(
            1 for i in range((end_of_month - start_date).days + 1)
            if (start_date + timedelta(days=i)).strftime('%A') in lesson_days
        )

        # 🔴 **Agar dars kuni bo‘lmasa, nolga bo‘linishdan qochish**
        if total_lessons_in_month == 0:
            total_payment_due = Decimal("0")
        else:
            per_lesson_price = Decimal(str(group.kurs.narxi)) / Decimal(total_lessons_in_month)
            total_payment_due = per_lesson_price * Decimal(attended_lessons)

        # **O‘quvchining oldin to‘lagan summasi**
        total_paid = cls.objects.filter(
            student=student, group=group, month=start_date.month, year=start_date.year
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal("0")

        # **Qolgan qarzdorlik**
        remaining_balance = max(total_payment_due - total_paid, Decimal("0"))

        return {
            'total_debt': int(total_payment_due),  # `Decimal` emas `int` qaytarish
            'remaining_balance': int(remaining_balance),
            'total_paid': int(total_paid),
            'total_lessons_in_month': total_lessons_in_month,
            'attended_lessons': attended_lessons,
        }