# Generated by Django 2.1.3 on 2019-01-08 00:29

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0015_auto_20190108_0028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopping',
            name='quantity',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='quantity'),
        ),
    ]
