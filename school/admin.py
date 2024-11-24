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
    # Ro'yxatda ko'rsatiladigan maydonlar
    list_display = (
        'id', 'viloyat', 'tuman', 'maktab_raqami', 'sharntoma_raqam', 'nomi', 'is_active', 'created_at', 'updated_at'
    )

    # Qidiruv maydonlari
    search_fields = ('nomi', 'maktab_raqami', 'viloyat', 'tuman')

    # Filtr paneli
    list_filter = ('viloyat', 'tuman', 'is_active', 'created_at')

    # Maydonlarga qarab tartib berish imkoniyati
    ordering = ('-created_at',)

    # Inline tahrirlash uchun maydonlar
    list_editable = ('is_active', 'maktab_raqami', 'sharntoma_raqam', 'nomi')

    # Yaratilgan vaqt va o'zgartirilgan vaqtlarni faqat o'qish uchun qilish
    readonly_fields = ('created_at', 'updated_at')

    # Harakatlar (actions) qo'shish
    actions = ['activate_maktab', 'deactivate_maktab', 'delete_selected_maktab']

    # Default pagination size
    list_per_page = 20

    def changelist_view(self, request, extra_context=None):
        """
        Custom changelist view to allow dynamic list_per_page.
        """
        # Check if 'list_per_page' is in GET parameters
        if 'list_per_page' in request.GET:
            try:
                # Update list_per_page dynamically
                self.list_per_page = int(request.GET.get('list_per_page', self.list_per_page))
            except ValueError:
                pass  # Ignore invalid values

        # Add custom context for the dropdown
        extra_context = extra_context or {}
        extra_context['per_page_options'] = [20, 100, 500, 1000]

        return super().changelist_view(request, extra_context)

    def activate_maktab(self, request, queryset):
        """
        Tanlangan maktablarni faol qilish
        """
        updated_count = queryset.update(is_active=True)
        self.message_user(request, f"{updated_count} maktab faol qilindi.")

    activate_maktab.short_description = "Tanlangan maktablarni faol qilish"

    def deactivate_maktab(self, request, queryset):
        """
        Tanlangan maktablarni nofaol qilish
        """
        updated_count = queryset.update(is_active=False)
        self.message_user(request, f"{updated_count} maktab nofaol qilindi.")

    deactivate_maktab.short_description = "Tanlangan maktablarni nofaol qilish"

    def delete_selected_maktab(self, request, queryset):
        """
        Tanlangan barcha maktablarni o'chirish
        """
        deleted_count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{deleted_count} maktab o'chirildi.")

    delete_selected_maktab.short_description = "Tanlangan maktablarni o'chirish"

# Sinf uchun alohida admin konfiguratsiya
@admin.register(Sinf)
class SinfAdmin(admin.ModelAdmin):
    list_display = ('maktab', 'sinf_raqami', 'belgisi', 'is_active', 'created_at', 'updated_at')
    list_filter = ('maktab__viloyat', 'maktab__tuman', 'belgisi', 'is_active', 'created_at')
    search_fields = ('maktab__maktab_raqami', 'sinf_raqami', 'belgisi__nomi')
    ordering = ('maktab', 'sinf_raqami')
    autocomplete_fields = ('maktab', 'belgisi')
