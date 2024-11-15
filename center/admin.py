from django.contrib import admin
from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from .models import Center, Images, Filial, Kasb, Yonalish, Kurs, E_groups, GroupMembership


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'rahbari')
    search_fields = ('nomi', 'rahbari__username')
    list_filter = ('nomi',)


@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'image', 'description')
    search_fields = ('title', 'user__username')
    list_filter = ('user',)


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ('center', 'location', 'contact', 'telegram', 'image')
    search_fields = ('location', 'center__nomi', 'contact')
    list_filter = ('center',)


@admin.register(Kasb)
class KasbAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'is_active', 'created_at', 'updated_at')
    search_fields = ('nomi',)
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active',)


@admin.register(Yonalish)
class YonalishAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'kasb', 'is_active', 'created_at', 'updated_at')
    search_fields = ('nomi', 'kasb__nomi')
    list_filter = ('kasb', 'is_active', 'created_at')
    list_editable = ('is_active',)


@admin.register(Kurs)
class KursAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'yonalish', 'narxi', 'is_active', 'created_at', 'updated_at')
    search_fields = ('nomi', 'yonalish__nomi')
    list_filter = ('yonalish', 'is_active', 'created_at')
    list_editable = ('is_active',)


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
