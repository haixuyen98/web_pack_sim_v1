from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.SeoFile)
class SeoFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'content')
    fields = ['name', 'content']

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "File xác thực"
    change_form_template = 'admin/sims/simstore/components/customize_warning.html'

@admin.register(models.SeoProduct)
class SeoProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'h1', 'description', 'c2', 'min_price', 'max_price')

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "SEO chi tiết loại Sim"
    change_form_template = 'admin/sims/simstore/components/customize_warning.html'   
