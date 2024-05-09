from django.apps import AppConfig


class SeoOptimizerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seo_optimizer'
    depends_on = ['blog']
    verbose_name = 'Tối ưu SEO'