# Generated by Django 5.0.2 on 2024-02-19 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0015_remove_profile_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ArticlePage',
        ),
    ]
