# Generated by Django 5.0.2 on 2024-02-29 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('theme_config', '0002_delete_mymodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vitual_names', models.CharField(max_length=100)),
                ('vitual_address', models.TextField()),
                ('vitual_sims', models.CharField(max_length=20)),
                ('vitual_times', models.CharField(max_length=20)),
            ],
        ),
    ]
