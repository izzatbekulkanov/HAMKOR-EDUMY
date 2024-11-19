from django.contrib import admin
from school.models import Maktab, Sinf, Belgisi
from account.models import Regions, District


# Belgisi uchun admin konfiguratsiya
@admin.register(Belgisi)
class BelgisiAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('nomi',)
    ordering = ('nomi',)


# Sinf uchun inline konfiguratsiya
class SinfInline(admin.TabularInline):
    model = Sinf
    extra = 1  # Qo'shimcha bitta bo'sh maydon ko'rsatiladi
    fields = ('sinf_raqami', 'belgisi', 'is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('belgisi',)
    show_change_link = True


# Maktab uchun admin konfiguratsiya
@admin.register(Maktab)
class MaktabAdmin(admin.ModelAdmin):
    list_display = ('maktab_raqami', 'viloyat', 'tuman', 'sharntoma_raqam', 'is_active', 'created_at', 'updated_at')
    list_filter = ('viloyat', 'tuman', 'is_active', 'created_at')
    search_fields = ('maktab_raqami', 'sharntoma_raqam')
    ordering = ('maktab_raqami',)
    autocomplete_fields = ('viloyat', 'tuman')
    inlines = [SinfInline]


# Sinf uchun alohida admin konfiguratsiya
@admin.register(Sinf)
class SinfAdmin(admin.ModelAdmin):
    list_display = ('maktab', 'sinf_raqami', 'belgisi', 'is_active', 'created_at', 'updated_at')
    list_filter = ('maktab__viloyat', 'maktab__tuman', 'belgisi', 'is_active', 'created_at')
    search_fields = ('maktab__maktab_raqami', 'sinf_raqami', 'belgisi__nomi')
    ordering = ('maktab', 'sinf_raqami')
    autocomplete_fields = ('maktab', 'belgisi')
