# Generated by Django 5.0.1 on 2024-01-27 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0006_tenanttemplates_link_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenanttemplates',
            name='link',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='tenanttemplates',
            name='theme_config_url',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
