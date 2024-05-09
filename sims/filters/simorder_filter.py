from django.contrib import admin
from sims.services.helpers import get_queryset_filter_date
from sims.common.choices import DATE_FILTER_CHOICES

class CustomCreatedAtFilter(admin.SimpleListFilter):
    title = 'Tạo lúc'
    parameter_name = 'createdAt'

    def lookups(self, request, model_admin):
        return DATE_FILTER_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        return get_queryset_filter_date(self.parameter_name,value,queryset)

class CustomPushedFilter(admin.SimpleListFilter):
    title = "Webhook status"
    parameter_name = 'pushed'

    def lookups(self, request, model_admin):
        return (
            ('success', ('Thành công')),
            ('failure', ('Thất bại')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'success':
            return queryset.filter(pushed=True)
        elif self.value() == 'failure':
            return queryset.filter(pushed=False)
