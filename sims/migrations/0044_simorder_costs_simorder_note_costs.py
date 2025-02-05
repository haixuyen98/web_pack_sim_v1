# Generated by Django 4.2.11 on 2024-04-17 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0043_alter_simorder_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='simorder',
            name='costs',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='Chi phí'),
        ),
        migrations.AddField(
            model_name='simorder',
            name='note_costs',
            field=models.CharField(blank=True, null=True, verbose_name='Ghi chú chi phí'),
        ),
    ]
