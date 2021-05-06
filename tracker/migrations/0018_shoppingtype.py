# Generated by Django 2.1.3 on 2019-01-08 03:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_auto_20190108_0312'),
        ('tracker', '0017_shopping_quantity_unit'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('privacy', models.PositiveSmallIntegerField(choices=[(0, 'INDIVIDUAL MEMBER DEPENDENT SHOPPING'), (1, 'ROOM MANAGER DEPENDENT SHOPPING')], default=0, verbose_name='SHOPPING TYPE CHOICES')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_shopping', to='rooms.Room', verbose_name='room')),
            ],
        ),
    ]