# Generated by Django 5.0.6 on 2024-11-08 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_alter_cashback_type'),
        ('center', '0002_e_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='kurs',
        ),
        migrations.AddField(
            model_name='customuser',
            name='e_groups',
            field=models.ManyToManyField(blank=True, to='center.e_groups', verbose_name='Kurslar'),
        ),
    ]