# Generated by Django 5.0.2 on 2024-02-26 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0009_simorder_browse_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simorder',
            name='attributes',
            field=models.JSONField(blank=True, default={}, null=True),
        ),
        migrations.AlterField(
            model_name='simorder',
            name='browse_history',
            field=models.TextField(blank=True, null=True),
        ),
    ]
