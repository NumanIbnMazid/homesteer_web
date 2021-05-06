# Generated by Django 2.1.3 on 2019-01-08 05:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_auto_20190108_0312'),
        ('tracker', '0021_auto_20190108_0514'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shopping',
            options={'ordering': ['-room__created_at'], 'verbose_name': 'Shopping', 'verbose_name_plural': 'Shoppings'},
        ),
        migrations.AddField(
            model_name='shopping',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_shopping_room', to='rooms.Room', verbose_name='room'),
        ),
    ]
