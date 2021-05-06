# Generated by Django 2.1.3 on 2019-01-03 11:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='title')),
                ('slug', models.SlugField(blank=True, unique=True, verbose_name='slug')),
                ('is_active', models.BooleanField(default=True, verbose_name='is_active')),
                ('privacy', models.PositiveSmallIntegerField(choices=[(0, 'Public'), (1, 'Members'), (2, 'Secret')], default=0, verbose_name='privacy')),
                ('description', models.TextField(blank=True, max_length=250, null=True, verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('creator', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
