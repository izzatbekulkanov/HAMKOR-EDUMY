from django.contrib import admin
from .models import SiteInfo, Season

@admin.register(SiteInfo)
class SiteInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin_name', 'site_type', 'is_active', 'created_at', 'updated_at')
    list_filter = ('site_type', 'is_active')
    search_fields = ('name', 'admin_name')

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('name', 'is_active')
    search_fields = ('name', 'additional_info')
