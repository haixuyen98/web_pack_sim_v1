# Generated by Django 4.2.11 on 2024-04-03 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0028_rename_amount_thu_accountreceivable_amount_payment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='simstore',
            name='t_detect',
            field=models.IntegerField(choices=[(1, 'viettel'), (2, 'vinaphone'), (3, 'mobifone'), (4, 'vietnamobile'), (5, 'gmobile'), (7, 'mayban'), (8, 'itelecom'), (9, 'wintel')], null=True, verbose_name='Nhà mạng hệ thống'),
        ),
    ]
