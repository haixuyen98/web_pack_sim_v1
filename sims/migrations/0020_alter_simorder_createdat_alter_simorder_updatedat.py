# Generated by Django 4.2.11 on 2024-03-20 07:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0019_simstore_iir_simstore_lpi_alter_simstore_ip_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simorder',
            name='createdAt',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Ngày tạo'),
        ),
        migrations.AlterField(
            model_name='simorder',
            name='updatedAt',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
