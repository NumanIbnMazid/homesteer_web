# Generated by Django 2.1.3 on 2019-01-10 02:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0030_totalholder_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopping',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='date'),
            preserve_default=False,
        ),
    ]
