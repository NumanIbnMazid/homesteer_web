# Generated by Django 2.1.3 on 2019-01-11 02:21

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0032_auto_20190110_0356'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shopping',
            name='total_cost',
        ),
        migrations.AddField(
            model_name='shopping',
            name='cost',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='cost'),
        ),
    ]
