from django.contrib import admin
from . import models

# Register your models here.

# @admin.register(models.SaleAlert)
# class SaleAlertAdmin(admin.ModelAdmin):
#     list_display = ('vitual_names', 'vitual_address', 'vitual_sims', 'vitual_times', 'message')
#     fields = ['vitual_names', 'vitual_address', 'vitual_sims', 'vitual_times']

#     def __init__(self, model, admin_site):
#         super().__init__(model, admin_site)
#         self.opts.verbose_name_plural = "Đơn hàng ảo" 
#         self.opts.app_label = "sims"