# Generated by Django 2.1.3 on 2019-01-10 00:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0026_remove_totalholder_meal_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='totalholder',
            name='cost_sector_total',
        ),
        migrations.RemoveField(
            model_name='totalholder',
            name='room',
        ),
        migrations.RemoveField(
            model_name='totalholder',
            name='shopping_total',
        ),
    ]