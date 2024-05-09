from django.contrib import admin
from sims.services.helpers import get_queryset_filter_date
from sims.common.choices import DATE_FILTER_CHOICES, CATEGORY_CHOICES

class CustomPublishFilter(admin.SimpleListFilter):
    title='Cập nhật lúc'
    parameter_name='publish'
  

    def lookups(self, request, model_admin):
        return DATE_FILTER_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        return get_queryset_filter_date(self.parameter_name, value, queryset)
        
class CustomPackFilter(admin.SimpleListFilter):
    title = 'Loại mạng'
    parameter_name = 'tt'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Trả trước'),
            ('2', 'Trả sau'),
            ('3', 'Không xác định'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if self.value() == '1' or self.value() == '2':
            return queryset.filter(tt=self.value())
        elif value == '3':
            return queryset.filter(tt=None)
        
class CustomStatusFilter(admin.SimpleListFilter):
    title = 'Trạng thái'
    parameter_name = 'h'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Đang hiển thị'),
            ('2', 'Đã ẩn'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if self.value() == '1':
            return queryset.filter(h=False)
        elif value == '2':
            return queryset.filter(h=True)
        
class CustomCateFilter(admin.SimpleListFilter):
    title = 'Loại sim'
    parameter_name = 'c'

    def lookups(self, request, model_admin):
        return CATEGORY_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            values = value.split(',')
            return queryset.filter(c__overlap=values)
        
class CustomPriceFilter(admin.SimpleListFilter):
    title = 'Khoảng giá'
    parameter_name = 'pn'

    def lookups(self, request, model_admin):
        return (
            ('1', '< 500 K'),
            ('2', '500 - 1 Tr'),
            ('3', '1 - 3 Tr'),
            ('4', '3 - 5 Tr'),
            ('5', '5 - 10 Tr'),
            ('6', '10 - 30 Tr'),
            ('7', '30 - 50 Tr'),
            ('8', '50 - 80 Tr'),
            ('9', '80 - 100 Tr'),
            ('10', '100 - 150 Tr'),
            ('11', '150 - 200 Tr'),
            ('12', '200 - 300 Tr'),
            ('13', '300 - 500 Tr'),
            ('14', '500 - 1 Tỷ'),
            ('15', '>= 1 Tỷ'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if self.value() == '1':
            return queryset.filter(**{'pn__lt': 500000})
        elif value == '2':
            return queryset.filter(**{'pn__gte': 500000, 'pn__lt':1000000})
        elif value == '3':
            return queryset.filter(**{'pn__gte': 1000000, 'pn__lt':3000000})
        elif value == '4':
            return queryset.filter(**{'pn__gte': 3000000, 'pn__lt':5000000})
        elif value == '5':
            return queryset.filter(**{'pn__gte': 5000000, 'pn__lt':10000000})
        elif value == '6':
            return queryset.filter(**{'pn__gte': 10000000, 'pn__lt':30000000})
        elif value == '7':
            return queryset.filter(**{'pn__gte': 30000000, 'pn__lt':50000000})
        elif value == '8':
            return queryset.filter(**{'pn__gte': 50000000, 'pn__lt':80000000})
        elif value == '9':
            return queryset.filter(**{'pn__gte': 80000000, 'pn__lt':100000000})
        elif value == '10':
            return queryset.filter(**{'pn__gte': 100000000, 'pn__lt':150000000})
        elif value == '11':
            return queryset.filter(**{'pn__gte': 150000000, 'pn__lt':200000000})
        elif value == '12':
            return queryset.filter(**{'pn__gte': 200000000, 'pn__lt':300000000})
        elif value == '13':
            return queryset.filter(**{'pn__gte': 300000000, 'pn__lt':500000000})
        elif value == '14':
            return queryset.filter(**{'pn__gte': 500000000, 'pn__lt':1000000000})
        elif value == '15':
            return queryset.filter(**{'pn__lte':1000000000})