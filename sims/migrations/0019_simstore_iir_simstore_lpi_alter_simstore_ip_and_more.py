# Generated by Django 4.2.11 on 2024-03-15 06:48

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0018_alter_simstore_c_alter_simstore_c2_alter_simstore_f_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='simstore',
            name='iir',
            field=models.IntegerField(blank=True, null=True, verbose_name='Lãi suất trả góp'),
        ),
        migrations.AddField(
            model_name='simstore',
            name='lpi',
            field=models.IntegerField(blank=True, null=True, verbose_name='Lãi suất trả chậm'),
        ),
        migrations.AlterField(
            model_name='simstore',
            name='ip',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), blank=True, null=True, size=None, verbose_name='Mua trả góp'),
        ),
        migrations.AlterField(
            model_name='simstore',
            name='it',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), blank=True, null=True, size=None, verbose_name='Thời hạn trả góp'),
        ),
        migrations.AlterField(
            model_name='simstore',
            name='k',
            field=models.CharField(blank=True, null=True, verbose_name='Gói cước'),
        ),
        migrations.AlterField(
            model_name='simstore',
            name='note',
            field=models.CharField(blank=True, null=True, verbose_name='Ghi chú'),
        ),
        migrations.AlterField(
            model_name='simstore',
            name='publish',
            field=models.DateTimeField(auto_now=True, verbose_name='Thời gian update'),
        ),
        migrations.AlterField(
            model_name='simstore',
            name='tt',
            field=models.IntegerField(blank=True, choices=[(1, 'Trả trước'), (2, 'Trả sau')], null=True, verbose_name='Loại mạng'),
        ),
    ]
