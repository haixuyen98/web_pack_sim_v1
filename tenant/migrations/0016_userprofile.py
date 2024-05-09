from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tenant', '0015_alter_tenant_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                # Define the fields of the UserProfile model
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assign_order', models.BooleanField(default=False)),
                ('is_current_assign', models.BooleanField(default=False)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'managed': True,  # Set managed to True to allow Django for managing the table
                'db_table': 'sims_userprofile',  # Specify the table name explicitly
            },
        ),
    ]
