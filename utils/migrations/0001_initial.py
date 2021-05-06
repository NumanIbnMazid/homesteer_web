# Generated by Django 2.1.3 on 2019-01-03 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, unique=True, verbose_name='slug')),
                ('category', models.CharField(blank=True, max_length=50, null=True, verbose_name='category')),
                ('notify_type', models.CharField(max_length=100, verbose_name='notification type')),
                ('identifier', models.CharField(blank=True, max_length=200, null=True, verbose_name='identifier')),
                ('room_identifier', models.CharField(blank=True, max_length=200, null=True, verbose_name='room identifier')),
                ('counter', models.PositiveSmallIntegerField(default=1, verbose_name='counter')),
                ('message', models.CharField(blank=True, max_length=200, null=True, verbose_name='message')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('receiver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_receiver', to='accounts.UserProfile', verbose_name='receiver')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_sender', to='accounts.UserProfile', verbose_name='sender')),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['updated_at'],
            },
        ),
    ]
