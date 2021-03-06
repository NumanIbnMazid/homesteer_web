# Generated by Django 2.1.3 on 2019-01-05 05:30

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0008_auto_20190105_0504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='totalholder',
            name='cost_sector_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='cost sector total'),
        ),
        migrations.AlterField(
            model_name='totalholder',
            name='meal_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='meal total'),
        ),
        migrations.AlterField(
            model_name='totalholder',
            name='shopping_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='shopping total'),
        ),
    ]
