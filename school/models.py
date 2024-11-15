from django.db import models
from account.models import Regions, District  # Regions va District modellari account appdan import qilindi


class Sinf(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="Sinfi")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")

    def __str__(self):
        return self.nomi


class Belgisi(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="Belgisi")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")

    def __str__(self):
        return self.nomi


class Maktab(models.Model):
    viloyat = models.ForeignKey(Regions, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Viloyat")
    tuman = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tuman")
    maktab_raqami = models.BigIntegerField(verbose_name="Maktab raqami")
    sinfi = models.ForeignKey(Sinf, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sinfi")
    belgisi = models.ForeignKey(Belgisi, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Belgisi")
    sharntoma_raqam = models.BigIntegerField(verbose_name="Sharntoma raqami")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")

    def __str__(self):
        return f"{self.maktab_raqami} - maktab"
