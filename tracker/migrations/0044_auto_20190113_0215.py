# Generated by Django 2.1.3 on 2019-01-13 02:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0043_auto_20190112_0358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppingtype',
            name='room',
        ),
        migrations.AlterModelOptions(
            name='shopping',
            options={'ordering': ['-created_by__room__created_at'], 'verbose_name': 'Shopping', 'verbose_name_plural': 'Shoppings'},
        ),
        migrations.DeleteModel(
            name='ShoppingType',
        ),
    ]
