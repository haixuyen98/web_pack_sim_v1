# Generated by Django 4.2.11 on 2024-05-08 12:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking_affiliate', '0006_customer_login_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='sim_status',
        ),
    ]
