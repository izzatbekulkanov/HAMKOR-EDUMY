from django.contrib import admin
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.html import format_html

from .models import Center, Images, Filial, Kasb, Yonalish, Kurs, E_groups, GroupMembership, SubmittedStudent, \
    StudentDetails, PaymentRecord


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'rahbari', 'get_schools', 'is_active', 'is_verified', 'all_views', 'created_at')
    search_fields = ('nomi', 'rahbari__username', 'rahbari__first_name', 'rahbari__last_name', 'maktab__nomi')
    list_filter = ('is_active', 'is_verified', 'all_views', 'maktab')  # Filterlarda `all_views` ni qo'shish
    filter_horizontal = ('maktab',)  # ManyToManyField uchun
    list_editable = ('is_active', 'is_verified', 'all_views')  # `all_views` maydonini tahrirlashga qo'shish
    readonly_fields = ('created_at', 'updated_at')  # Faqat o'qish uchun maydonlar

    def get_schools(self, obj):
        """
        Maktablar ro'yxatini qaytaradi.
        """
        schools = obj.maktab.all()
        if schools:
            return format_html("<br>".join([school.nomi for school in schools]))
        return "Maktablar yo'q"

    get_schools.short_description = "Maktablar"

    def save_model(self, request, obj, form, change):
        """
        Modelni saqlash vaqtida foydalanuvchi faoliyatini kuzatish.
        """
        if not obj.rahbari:
            obj.rahbari = request.user  # Agar rahbar belgilanmagan bo'lsa, joriy foydalanuvchini rahbar qilib belgilang
        super().save_model(request, obj, form, change)


@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'image', 'description')
    search_fields = ('title', 'user__username')
    list_filter = ('user',)


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    # Jadvaldagi ustunlar
    list_display = ('center', 'location', 'contact', 'telegram', 'admin_list', 'created_at')

    # Filtrlash uchun maydonlar
    list_filter = ('center', 'created_at')

    # Qidiruv uchun maydonlar
    search_fields = ('location', 'center__nomi', 'contact')

    # ManyToManyField uchun boshqaruv interfeysi
    filter_horizontal = ('admins',)

    # Read-only maydonlar
    readonly_fields = ('created_at',)

    # Adminlar ro'yxatini ko'rsatish uchun yordamchi funksiya
    def admin_list(self, obj):
        return ", ".join([admin.username or admin.email for admin in obj.admins.all()])
    admin_list.short_description = "Administratorlar"

    # Ma'lumot tahriri uchun formalar
    fieldsets = (
        ('Umumiy ma’lumotlar', {
            'fields': ('center', 'location', 'contact', 'telegram', 'image', 'images')
        }),
        ('Administratorlar', {
            'fields': ('admins',)
        }),
        ('Qo‘shimcha ma’lumotlar', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Kasb)
class KasbAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'is_active', 'created_at', 'updated_at')
    search_fields = ('nomi',)
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active',)


@admin.register(Yonalish)
class YonalishAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'kasb', 'center', 'is_active', 'created_at', 'updated_at')
    search_fields = ('nomi', 'kasb__nomi', 'center__nomi')
    list_filter = ('kasb', 'center', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    autocomplete_fields = ('kasb', 'center', 'kurslar')
    filter_horizontal = ('kurslar',)


@admin.register(Kurs)
class KursAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'narxi', 'center', 'is_active', 'created_at', 'updated_at')
    search_fields = ('nomi', 'center__nomi')
    list_filter = ('center', 'is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    autocomplete_fields = ('center',)



class E_groupsAdminForm(forms.ModelForm):
    days_of_week = forms.MultipleChoiceField(
        choices=E_groups.DAYS_OF_WEEK,
        widget=CheckboxSelectMultiple,
        required=False,
        label="Dars kunlari"
    )

    class Meta:
        model = E_groups
        fields = '__all__'


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1
    fields = ('student', 'is_active', 'joined_at')
    readonly_fields = ('joined_at',)


@admin.register(E_groups)
class E_groupsAdmin(admin.ModelAdmin):
    form = E_groupsAdminForm
    list_display = ('group_name', 'kurs', 'get_days_of_week_display', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at', 'kurs')
    search_fields = ('group_name', 'kurs__nomi')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    inlines = [GroupMembershipInline]

    fieldsets = (
        (None, {
            'fields': ('group_name', 'kurs', 'days_of_week', 'is_active')
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_days_of_week_display(self, obj):
        return obj.get_days_of_week_display()
    get_days_of_week_display.short_description = "Dars kunlari"

    @admin.action(description="Tanlangan guruhlarni faollashtirish")
    def activate_groups(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} guruh(lar) faollashtirildi.")

    @admin.action(description="Tanlangan guruhlarni nofaol qilish")
    def deactivate_groups(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} guruh(lar) nofaol qilindi.")

    actions = [activate_groups, deactivate_groups]


@admin.register(SubmittedStudent)
class SubmittedStudentAdmin(admin.ModelAdmin):
    # Jadvalda ko'rinadigan ustunlar
    list_display = (
        'first_name', 'last_name', 'phone_number', 'sinf', 'belgisi',
        'kasb', 'yonalish', 'status', 'created_at', 'added_by', 'display_kurslar'
    )

    # Filtrlash imkoniyatlari
    list_filter = (
        'status', 'sinf__maktab', 'kasb', 'yonalish',
        'created_at', 'added_by', 'kurslar'
    )

    # Qidiruv maydonlari
    search_fields = (
        'first_name', 'last_name', 'belgisi', 'kasb__nomi', 'yonalish__nomi', 'phone_number', 'kurslar__nomi'
    )

    # Inline tahrirlash imkoniyatlari
    list_editable = ('status',)

    # Har bir yozuvni tartibga solish bo'yicha sozlamalar
    ordering = ('-created_at',)

    # Bir sahifadagi yozuvlar sonini cheklash
    list_per_page = 25

    # Qo'shimcha amallar
    actions = ['mark_as_accepted', 'mark_as_rejected']

    # Custom Actions
    def mark_as_accepted(self, request, queryset):
        queryset.update(status='accepted')
        self.message_user(request, "Tanlangan o'quvchilar holati 'Qabul qilingan' deb belgilandi.")
    mark_as_accepted.short_description = "Tanlanganlarni 'Qabul qilingan' holatiga o'tkazish"

    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Tanlangan o'quvchilar holati 'Rad etilgan' deb belgilandi.")
    mark_as_rejected.short_description = "Tanlanganlarni 'Rad etilgan' holatiga o'tkazish"

    # Qo'shimcha ma'lumot maydoni
    readonly_fields = ('created_at', 'updated_at')

    # Forma tahriri
    fieldsets = (
        ('Shaxsiy ma’lumotlar', {
            'fields': ('first_name', 'last_name', 'phone_number', 'belgisi')
        }),
        ('Bog‘langan ma’lumotlar', {
            'fields': ('sinf', 'kasb', 'yonalish', 'kurslar')
        }),
        ('Holat va Meta', {
            'fields': ('status', 'created_at', 'updated_at', 'added_by')
        }),
    )

    # ManyToManyField uchun ko'rinadigan qiymatlarni sozlash
    def display_kurslar(self, obj):
        """Display a comma-separated list of courses."""
        return ", ".join([kurs.nomi for kurs in obj.kurslar.all()])
    display_kurslar.short_description = 'Kurslar'


@admin.register(StudentDetails)
class StudentDetailsAdmin(admin.ModelAdmin):
    # Jadvalda ko'rinadigan ustunlar
    list_display = (
        'student', 'student_status', 'birth_date', 'gender', 'region', 'district',
        'parent_name', 'parent_phone', 'previous_school', 'created_at'
    )

    # Filtrlash imkoniyatlari
    list_filter = (
        'gender', 'region', 'district', 'created_at', 'student__status',
    )

    # Qidiruv maydonlari
    search_fields = (
        'student__first_name', 'student__last_name', 'student__phone_number',
        'parent_name', 'region', 'district', 'previous_school'
    )

    # Har bir yozuvni tartibga solish bo'yicha sozlamalar
    ordering = ('-created_at',)

    # Bir sahifadagi yozuvlar sonini cheklash
    list_per_page = 20

    # Qo'shimcha ma'lumot maydoni
    readonly_fields = ('created_at', 'updated_at', 'student_status', 'student_phone')

    # Inline tahrirlash imkoniyatlari
    list_editable = ('gender', 'region', 'district')

    # Forma tahriri
    fieldsets = (
        ('Shaxsiy ma’lumotlar', {
            'fields': ('student', 'student_status', 'student_phone', 'birth_date', 'gender', 'address', 'region', 'district')
        }),
        ('Ota-ona ma’lumotlari', {
            'fields': ('parent_name', 'parent_phone', 'relationship_to_student')
        }),
        ('Qo‘shimcha ma’lumotlar', {
            'fields': ('previous_school', 'medical_conditions', 'hobbies', 'social_media_link', 'photo')
        }),
        ('Holat va Meta', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    # Tasdiqlash (Save) paytida qo‘shimcha validatsiya
    def save_model(self, request, obj, form, change):
        if obj.parent_phone and not obj.parent_phone.startswith('+998'):
            raise ValueError("Telefon raqami +998 bilan boshlanishi kerak.")
        super().save_model(request, obj, form, change)

    # Qo'shimcha SubmittedStudent ma'lumotlari
    def student_status(self, obj):
        """SubmittedStudent holatini ko'rsatadi."""
        return obj.student.get_status_display()
    student_status.short_description = "Holati"

    def student_phone(self, obj):
        """SubmittedStudent telefon raqamini ko'rsatadi."""
        return obj.student.phone_number
    student_phone.short_description = "Telefon raqami"

    # O'quvchining ismi bilan ko'rsatish
    def student(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    student.short_description = "O'quvchi"


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'group', 'amount_paid', 'total_debt', 'remaining_balance', 'payment_date',
        'attended_lessons', 'total_lessons_in_month', 'status_display', 'month', 'year', 'course_total_price'
    )
    list_filter = ('group', 'month', 'year')
    search_fields = ('student__first_name', 'student__last_name', 'group__group_name')
    date_hierarchy = 'payment_date'
    ordering = ('-payment_date',)

    readonly_fields = (
        'payment_date', 'remaining_balance', 'total_debt', 'attended_lessons',
        'total_lessons_in_month', 'course_total_price'
    )

    def status_display(self, obj):
        """O'quvchining qarzdorligini rangli ko'rinishda chiqarish"""
        if obj.remaining_balance == 0:
            color = "green"
            text = "To‘lov to‘liq qilingan"
        else:
            color = "red"
            text = f"Qoldiq qarz: {obj.remaining_balance} so‘m"
        return format_html('<span style="color: {};">{}</span>', color, text)

    status_display.short_description = "Holati"

    actions = ["mark_as_fully_paid"]

    def mark_as_fully_paid(self, request, queryset):
        """Tanlangan to‘lovlarni to‘liq to‘langan deb belgilash"""
        queryset.update(remaining_balance=0)
        self.message_user(request, "Tanlangan to‘lovlar to‘liq qilingan deb belgilandi.")

    mark_as_fully_paid.short_description = "To‘lovni to‘liq qilingan deb belgilash"