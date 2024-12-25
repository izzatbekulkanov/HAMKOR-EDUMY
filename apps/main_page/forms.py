from django import forms
from .models import SiteInfo, Season

class SiteInfoForm(forms.ModelForm):
    class Meta:
        model = SiteInfo
        fields = ['name', 'admin_name', 'site_type', 'is_active']

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['name', 'css_code', 'js_code', 'additional_info', 'is_active']
