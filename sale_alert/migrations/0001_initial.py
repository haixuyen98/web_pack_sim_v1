# Generated by Django 5.0.1 on 2024-02-21 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SaleAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vitual_names', models.TextField()),
                ('vitual_address', models.TextField()),
                ('vitual_sims', models.TextField()),
                ('vitual_times', models.TextField()),
            ],
        ),
    ]
