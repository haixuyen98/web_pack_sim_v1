# Generated by Django 4.2.8 on 2024-01-15 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_article_excerpt_alter_article_meta_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='excerpt',
            field=models.TextField(blank=True, null=True),
        ),
    ]
