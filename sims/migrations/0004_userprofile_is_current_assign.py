# Generated by Django 5.0.1 on 2024-02-16 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0003_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_current_assign',
            field=models.BooleanField(default=False),
        ),
    ]
