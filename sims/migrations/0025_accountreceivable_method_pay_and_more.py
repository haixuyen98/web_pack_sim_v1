# Generated by Django 4.2.11 on 2024-03-29 08:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0024_remove_accountreceivable_created_at2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountreceivable',
            name='method_pay',
            field=models.CharField(blank=True, null=True, verbose_name='Hình thức thanh toán'),
        ),
        migrations.AddField(
            model_name='accountreceivable',
            name='user_create',
            field=models.CharField(blank=True, null=True, verbose_name='Người tạo'),
        ),
        migrations.AlterField(
            model_name='accountreceivable',
            name='amount_thu',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Số tiền thanh toán'),
        ),
        migrations.AlterField(
            model_name='accountreceivable',
            name='transfer_at',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Ngày tạo'),
        ),
    ]
