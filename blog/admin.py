from django.contrib import admin
from . import models
from django.db.models import Q
from django.utils.translation import gettext as _
from .widget import CustomHTMLSlug

@admin.register(models.Article)
class ArticlePostAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'slug' in form.base_fields:
            form.base_fields['slug'].widget = CustomHTMLSlug(form)
        return form

    list_display = ('title', 'status', 'slug', 'user', 'publishedAt')
    list_filter = ('user', 'status', 'category', 'publishedAt')
    search_fields = ["title", "excerpt"]
    exclude = ["type"]
    fieldsets = (
        (_('Thông tin chung'), {
           'fields': ('title', 'slug', 'tags', 'featured', 'excerpt', 'featured_image', 'body', 'publishedAt','category', 'status')
        }),
        (_('Seo Meta'), {
            'classes': ('collapse', 'open'),
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'meta_canonical','related_pages', 'headscript'),
        }),
    )
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "Bài Viết"
    change_form_template = 'admin/sims/simstore/components/customize_warning.html'
        
    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            Q(type=models.Article.Type.POST)
        )

    # prepopulated_fields = {'slug': ('title',), }

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)
    
@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    # list_display = ('name')

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "Từ Khoá"
    change_form_template = 'admin/sims/simstore/components/customize_warning.html' 

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'slug' in form.base_fields:
            form.base_fields['slug'].widget = CustomHTMLSlug(form)
        return form
    
    list_display = ('name', 'slug', 'timestamp')

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "Danh mục"
    change_form_template = 'admin/sims/simstore/components/customize_warning.html'

    # prepopulated_fields = {'slug': ('name',), }
