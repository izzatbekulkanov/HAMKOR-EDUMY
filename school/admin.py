from django.contrib import admin
from .models import Sinf, Belgisi, Maktab


@admin.register(Sinf)
class SinfAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('nomi',)
    ordering = ('nomi',)
    list_editable = ('is_active',)


@admin.register(Belgisi)
class BelgisiAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('nomi',)
    ordering = ('nomi',)
    list_editable = ('is_active',)


@admin.register(Maktab)
class MaktabAdmin(admin.ModelAdmin):
    list_display = ('maktab_raqami', 'viloyat', 'tuman', 'sinfi', 'belgisi', 'sharntoma_raqam', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'viloyat', 'tuman')
    search_fields = ('maktab_raqami', 'sharntoma_raqam', 'viloyat__name', 'tuman__name')
    ordering = ('maktab_raqami',)
    list_editable = ('is_active',)
