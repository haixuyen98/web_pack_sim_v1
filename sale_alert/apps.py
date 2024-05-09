from django.apps import AppConfig


class OrderFakingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sale_alert'
    depends_on = ['sims']