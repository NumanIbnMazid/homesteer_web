# Generated by Django 2.1.3 on 2019-01-24 00:43

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0001_initial'),
        ('tracker', '0046_auto_20190124_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashDeposit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20, null=True, verbose_name='title')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='amount')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_deposit', to='memberships.Membership', verbose_name='member')),
            ],
            options={
                'verbose_name': 'Cash Deposit',
                'verbose_name_plural': 'Cash Deposits',
                'ordering': ['-member__room__created_at'],
            },
        ),
        migrations.RemoveField(
            model_name='totalholder',
            name='deposit_amount',
        ),
        migrations.RemoveField(
            model_name='totalholder',
            name='deposit_title',
        ),
    ]
