from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, Gender, Regions, District, Quarters, Roles, Cashback, UserActivity


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = (
        'username', 'email', 'first_name', 'second_name', 'user_type', 'is_active', 'created_at', 'updated_at'
    )
    list_filter = ('user_type', 'is_active', 'created_at', 'roles')
    search_fields = ('username', 'email', 'first_name', 'second_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions', 'roles', 'cashback', 'e_groups')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'last_logout')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Shaxsiy ma\'lumotlar', {'fields': ('first_name', 'second_name', 'third_name', 'birth_date', 'gender', 'phone_number')}),
        ('Qo\'shimcha ma\'lumotlar', {'fields': ('p_first_name', 'p_second_name', 'p_phone_number', 'passport_serial', 'passport_jshshir')}),
        ('Hududiy ma\'lumotlar', {'fields': ('regions', 'district', 'quarters', 'address')}),
        ('Ijtimoiy tarmoqlar', {'fields': ('telegram', 'instagram', 'facebook')}),
        ('Foydalanuvchi turi va roli', {'fields': ('user_type', 'roles', 'now_role')}),
        ('Muayyan sanalar', {'fields': ('last_login', 'last_logout', 'created_at', 'updated_at')}),
        ('Faollik', {'fields': ('is_active', 'cashback', 'e_groups')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'user_type'),
        }),
    )

    @admin.action(description="Tanlangan foydalanuvchilarni faollashtirish")
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} foydalanuvchi(lar) faollashtirildi.")

    @admin.action(description="Tanlangan foydalanuvchilarni nofaol qilish")
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} foydalanuvchi(lar) nofaol qilindi.")

    actions = [activate_users, deactivate_users]


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
    list_display = ('name', 'type', 'user_type', 'summasi', 'is_active', 'created_at', 'updated_at')
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
            'fields': ('name', 'summasi', 'type', 'user_type')
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
