# Generated by Django 2.1.3 on 2019-01-12 03:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0040_auto_20190112_0343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopping',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_shopping', to='memberships.Membership', verbose_name='created by'),
        ),
    ]