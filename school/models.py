from django.db import models


class Belgisi(models.Model):
    nomi = models.CharField(max_length=255, verbose_name="Belgisi")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")

    def __str__(self):
        return self.nomi


class Maktab(models.Model):
    viloyat = models.CharField(max_length=255, null=True, blank=True, verbose_name="Viloyat")
    tuman = models.CharField(max_length=255, null=True, blank=True, verbose_name="tuman")
    maktab_raqami = models.BigIntegerField(verbose_name="Maktab raqami", null=True, blank=True)
    sharntoma_raqam = models.BigIntegerField(verbose_name="Sharntoma raqami", null=True, blank=True)
    nomi = models.CharField(max_length=255, verbose_name="Nomi", null=True, blank=True)

    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")

    def __str__(self):
        return f"{self.maktab_raqami} - maktab"


class Sinf(models.Model):
    maktab = models.ForeignKey('school.Maktab',on_delete=models.CASCADE,related_name='sinflar',verbose_name="Maktab")
    sinf_raqami = models.CharField(max_length=50, verbose_name="Sinf raqami")
    belgisi = models.ForeignKey('school.Belgisi',on_delete=models.SET_NULL,null=True,blank=True,verbose_name="Belgisi")
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan vaqti")

    def __str__(self):
        return f"{self.sinf_raqami} - {self.maktab.maktab_raqami if self.maktab else 'Maktab yo\'q'}"
