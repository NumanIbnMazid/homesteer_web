# Generated by Django 2.1.3 on 2019-01-05 02:50

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0003_remove_membertrack_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackerfield',
            name='cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='cost'),
        ),
    ]