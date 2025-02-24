from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from .models import CustomUser, Gender, Regions, District, Quarters, Roles, Cashback, UserActivity, CashbackRecord


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = (
        'username', 'email', 'first_name', 'second_name', 'maktab',
        'user_type', 'is_verified', 'is_active', 'cashback_records_count',
    )
    list_filter = ('user_type', 'is_verified', 'is_active', 'created_at', 'roles', 'maktab')
    search_fields = (
    'username', 'email', 'first_name', 'second_name', 'maktab__nomi', 'maktab__viloyat', 'maktab__tuman')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions', 'roles', 'cashback', 'e_groups')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'last_logout', 'image_preview')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'imageFile', 'image_preview')}),
        ('Shaxsiy ma\'lumotlar',
         {'fields': ('first_name', 'second_name', 'third_name', 'birth_date', 'gender', 'phone_number')}),

        ('Qo\'shimcha ma\'lumotlar',
         {'fields': ('p_first_name', 'p_second_name', 'p_phone_number', 'passport_serial', 'passport_jshshir')}),

        ('Hududiy ma\'lumotlar', {'fields': ('regions', 'district', 'quarters', 'address')}),

        ('Maktab ma\'lumotlari', {'fields': ('maktab',)}),

        ('Ijtimoiy tarmoqlar', {'fields': ('telegram', 'instagram', 'facebook')}),

        ('Foydalanuvchi turi va roli', {'fields': ('user_type', 'roles', 'now_role')}),

        ('Muayyan sanalar', {'fields': ('last_login', 'last_logout', 'created_at', 'updated_at')}),

        ('Faollik va tasdiqlash', {'fields': ('is_active', 'is_verified', 'cashback', 'e_groups')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'imageFile')}),
        ('Shaxsiy ma\'lumotlar',
         {'fields': ('first_name', 'second_name', 'third_name', 'birth_date', 'gender', 'phone_number')}),

        ('Qo\'shimcha ma\'lumotlar',
         {'fields': ('p_first_name', 'p_second_name', 'p_phone_number', 'passport_serial', 'passport_jshshir')}),

        ('Hududiy ma\'lumotlar', {'fields': ('regions', 'district', 'quarters', 'address')}),

        ('Ijtimoiy tarmoqlar', {'fields': ('telegram', 'instagram', 'facebook')}),

        ('Foydalanuvchi turi va roli', {'fields': ('user_type', 'roles', 'now_role')}),

        ('Faollik va tasdiqlash', {'fields': ('is_active', 'is_verified', 'cashback', 'e_groups')}),
    )

    @admin.display(description="Rasm")
    def image_preview(self, obj):
        if obj.imageFile:
            return mark_safe(
                f'<img src="{obj.imageFile.url}" style="width: 50px; height: 50px; border-radius: 5px;" />')
        return "Rasm yo'q"

    @admin.display(description="Cashback yozuvlari soni")
    def cashback_records_count(self, obj):
        if obj.user_type != "2":  # Faqat o'qituvchilar uchun ko'rsatamiz
            return "Foydalanilmaydi"

        # Foydalanuvchiga tegishli cashback yozuvlari sonini hisoblash
        count = CashbackRecord.objects.filter(teacher=obj).count()
        if count == 0:
            return "Cashback yozuvlari yo'q"

        return f"{count} ta cashback yozuvi"

    @admin.action(description="Tanlangan foydalanuvchilarni faollashtirish")
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} foydalanuvchi(lar) faollashtirildi.")

    @admin.action(description="Tanlangan foydalanuvchilarni nofaol qilish")
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} foydalanuvchi(lar) nofaol qilindi.")

    @admin.action(description="Tanlangan foydalanuvchilarni tasdiqlash")
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} foydalanuvchi(lar) tasdiqlandi.")

    @admin.action(description="Tanlangan foydalanuvchilarni tasdiqlashni bekor qilish")
    def unverify_users(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} foydalanuvchi(lar) tasdiqlash bekor qilindi.")

    actions = [activate_users, deactivate_users, verify_users, unverify_users]


@admin.register(CashbackRecord)
class CashbackRecordAdmin(admin.ModelAdmin):
    list_display = ('cashback', 'teacher', 'student', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'cashback__type', 'teacher__user_type')
    search_fields = ('cashback__name', 'teacher__first_name', 'student__first_name')
    ordering = ('-created_at',)
    actions = ['mark_as_paid', 'mark_as_unpaid']

    @admin.action(description="Tanlangan cashback yozuvlarini to'langan deb belgilash")
    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
        self.message_user(request, f"{queryset.count()} cashback yozuvlari to'langan deb belgilandi.")

    @admin.action(description="Tanlangan cashback yozuvlarini to'lanmagan deb belgilash")
    def mark_as_unpaid(self, request, queryset):
        queryset.update(is_paid=False)
        self.message_user(request, f"{queryset.count()} cashback yozuvlari to'lanmagan deb belgilandi.")


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('name',)


@admin.register(Regions)
class RegionsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)


@admin.register(Quarters)
class QuartersAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'district')
    list_filter = ('district',)
    search_fields = ('name',)


@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('name',)


@admin.register(Cashback)
class CashbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'user_type', 'summasi', 'parent_summ', 'is_active', 'created_at', 'updated_at')
    list_filter = ('type', 'user_type', 'is_active', 'created_at')
    search_fields = ('name', 'type', 'user_type')
    list_editable = ('is_active', 'summasi')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    actions = ['activate_cashbacks', 'deactivate_cashbacks']
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('name', 'summasi', 'parent_summ', 'type', 'user_type', 'center')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.display(description="Type (Verbose)")
    def display_type_verbose(self, obj):
        return dict(self.model.type_choices).get(obj.type, obj.type)

    @admin.action(description='Activate selected Cashbacks')
    def activate_cashbacks(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} cashback(s) activated.')

    @admin.action(description='Deactivate selected Cashbacks')
    def deactivate_cashbacks(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} cashback(s) deactivated.')


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time')
    list_filter = ('login_time', 'logout_time')
    search_fields = ('user__username', 'user__email')
