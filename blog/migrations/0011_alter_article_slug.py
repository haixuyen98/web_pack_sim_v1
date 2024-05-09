# Generated by Django 4.2.8 on 2024-01-17 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_alter_article_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.SlugField(max_length=250, unique=True, unique_for_date='publishedAt'),
        ),
    ]
