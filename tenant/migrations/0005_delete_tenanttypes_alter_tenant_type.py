# Generated by Django 5.0.1 on 2024-01-27 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0004_alter_tenanttemplates_tenant_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenant',
            name='type',
            field=models.CharField(choices=[], default='public', max_length=100),
        ),
    ]
