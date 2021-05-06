# Generated by Django 2.1.3 on 2019-01-05 23:24

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0009_auto_20190105_0530'),
    ]

    operations = [
        migrations.AddField(
            model_name='totalholder',
            name='cash_deposit',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='cash deposit'),
        ),
    ]