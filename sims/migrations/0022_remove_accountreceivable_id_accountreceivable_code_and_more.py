# Generated by Django 4.2.11 on 2024-03-22 13:47

from django.db import migrations, models
import django.utils.timezone
import sims.models


class Migration(migrations.Migration):

    dependencies = [
        ('sims', '0021_alter_simstore_h_accountreceivable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountreceivable',
            name='id',
        ),
        migrations.AddField(
            model_name='accountreceivable',
            name='code',
            field=models.CharField(default=sims.models.AccountReceivable.generate_unique_code, editable=False, max_length=20, primary_key=True, serialize=False, unique=True, verbose_name='Mã'),
        ),
        migrations.AlterField(
            model_name='accountreceivable',
            name='amount_chi',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='accountreceivable',
            name='amount_thu',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='accountreceivable',
            name='created_at',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Ngày tạo'),
        ),
        migrations.AlterField(
            model_name='accountreceivable',
            name='transfer_at',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Ngày chuyển'),
        ),
    ]
