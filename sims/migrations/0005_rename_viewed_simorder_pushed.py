# Generated by Django 5.0.1 on 2024-02-16 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0004_userprofile_is_current_assign'),
    ]

    operations = [
        migrations.RenameField(
            model_name='simorder',
            old_name='viewed',
            new_name='pushed',
        ),
    ]
