# Generated by Django 4.2.11 on 2024-04-12 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seo_optimizer', '0011_alter_seofile_content_alter_seofile_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='articlepage',
            options={'verbose_name': 'seo page'},
        ),
        migrations.AlterModelOptions(
            name='seoproduct',
            options={'verbose_name': 'SEO chi tiết loại Sim'},
        ),
    ]
