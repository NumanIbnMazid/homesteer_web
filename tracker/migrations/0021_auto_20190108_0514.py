# Generated by Django 2.1.3 on 2019-01-08 05:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0020_auto_20190108_0334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopping',
            name='member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_shopping', to='memberships.Membership', verbose_name='member'),
        ),
    ]
