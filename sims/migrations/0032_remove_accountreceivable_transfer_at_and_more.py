# Generated by Django 4.2.11 on 2024-04-08 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0031_remove_accountreceivable_transfer_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountreceivable',
            name='transfer_at',
        ),
        migrations.AlterField(
            model_name='simorder',
            name='pushed',
            field=models.BooleanField(default=False, verbose_name='Push đơn'),
        ),
    ]
