# Generated by Django 2.1.3 on 2019-01-10 00:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0027_auto_20190110_0041'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='totalholder',
            options={'ordering': ['-member__room__created_at'], 'verbose_name': 'Total Holder', 'verbose_name_plural': 'Total Holders'},
        ),
    ]
