# Generated by Django 2.1.3 on 2019-01-13 03:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0005_auto_20190113_0252'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagerialSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shopping_type', models.PositiveSmallIntegerField(choices=[(0, 'INDIVIDUAL MEMBER DEPENDENT SHOPPING'), (1, 'ROOM MANAGER DEPENDENT SHOPPING')], default=0, verbose_name='shopping type')),
                ('is_CUD_able', models.BooleanField(default=True, verbose_name='is CUD able')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managerial_setting', to='rooms.Room', verbose_name='room')),
            ],
            options={
                'verbose_name': 'Managerial Setting',
                'verbose_name_plural': 'Managerial Settings',
                'ordering': ['-room__created_at'],
            },
        ),
        migrations.RemoveField(
            model_name='roomsetting',
            name='room',
        ),
        migrations.DeleteModel(
            name='RoomSetting',
        ),
    ]
