# Generated by Django 2.1.3 on 2019-01-03 11:10

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rooms', '0001_initial'),
        ('memberships', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, unique=True, verbose_name='slug')),
                ('meal_today', models.DecimalField(decimal_places=2, max_digits=4, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='meal today')),
                ('meal_next_day', models.DecimalField(decimal_places=2, max_digits=4, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='meal next day')),
                ('auto_entry', models.BooleanField(default=True, verbose_name='auto entry')),
                ('auto_entry_value', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='auto entry value')),
                ('meal_date', models.DateField(blank=True, null=True, verbose_name='meal date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('confirmed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='confirmed_by', to='memberships.Membership', verbose_name='confirmed by')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_meal', to='memberships.Membership', verbose_name='member')),
            ],
            options={
                'verbose_name': 'Meal Entry',
                'verbose_name_plural': 'Meal Entries',
                'ordering': ['member__room'],
            },
        ),
        migrations.CreateModel(
            name='MealUpdateRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, unique=True, verbose_name='slug')),
                ('meal_should_be', models.DecimalField(decimal_places=2, max_digits=4, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='meal should be')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_meal_update', to='memberships.Membership', verbose_name='member')),
                ('request_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_to', to='memberships.Membership', verbose_name='request to')),
            ],
            options={
                'verbose_name': 'Meal Update Request',
                'verbose_name_plural': 'Meal Update Requests',
                'ordering': ['member__room'],
            },
        ),
        migrations.CreateModel(
            name='MemberTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='cost')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_track', to='memberships.Membership', verbose_name='member')),
            ],
            options={
                'verbose_name': 'Member Track',
                'verbose_name_plural': 'Member Tracks',
                'ordering': ['-member__room__created_at'],
            },
        ),
        migrations.CreateModel(
            name='TrackerField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='title')),
                ('slug', models.SlugField(blank=True, unique=True, verbose_name='slug')),
                ('description', models.TextField(blank=True, max_length=60, null=True, verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated_at')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracker_field_room', to='rooms.Room', verbose_name='room')),
            ],
            options={
                'verbose_name': 'Cost Sector',
                'verbose_name_plural': 'Cost Sectors',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddField(
            model_name='membertrack',
            name='tracker_field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_track_field', to='tracker.TrackerField', verbose_name='cost sector'),
        ),
    ]
