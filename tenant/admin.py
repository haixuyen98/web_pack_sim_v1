from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from django_tenants.utils import get_public_schema_name
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from .models import Domain, Tenant, TenantTemplates
from .forms import TenantCloneForm
import uuid 

class DomainInline(admin.TabularInline):
    model = Domain
    max_num = 3
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_active', 'is_staff', 'is_superuser', 'get_groups']
    actions=['delete_selected']
    def delete_selected(self, request, queryset):
        if queryset.filter(username='admin').exists():
            self.message_user(request, "Deleting admin users is not allowed.", level='error')
        elif hasattr(request, 'tenant'):
            for user in queryset:
                user.is_active = False
                user.save()
        else:
            for user in queryset:
                user.is_active = False
                user.save()
    delete_selected.short_description = "Xoá tài khoản"
    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Nhóm'


@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    inlines = [DomainInline]
    def _only_public_tenant_access(self, request):
        try:
            return True if request.tenant.schema_name == get_public_schema_name() else False
        except AttributeError:
            return True
        
    def has_view_permission(self, request, view=None):
        return self._only_public_tenant_access(request)

    def has_add_permission(self, request, view=None):
        return self._only_public_tenant_access(request)
    
    def has_change_permission(self, request, view=None):
        return self._only_public_tenant_access(request)

    def has_delete_permission(self, request, view=None):
        return self._only_public_tenant_access(request)

    def has_view_or_change_permission(self, request, view=None):
        return self._only_public_tenant_access(request)

class TenantAdminOverrideAdmin(TenantAdmin):
    form = TenantCloneForm
    list_display = (
        "site_name",
        "phone",
        "schema_name",
        "paid_until",
        "is_active",
        "on_trial",
        "created_on",
        "is_template",
        "is_default"
    )

    readonly_fields = ('schema_name',)
    exclude = ('theme_config', 'config',)
    actions=['delete_selected']
    class Media:
        js = ('admin/js/my_custom_script.js',)  # Path to your custom JavaScript file

    def delete_selected(self, request, queryset):
        if queryset.filter(is_template=True).exists():
            self.message_user(request, "Deleting tenant (template) is not allowed.", level='error')
        else:
            queryset.delete()
            self.message_user(request, "Successfully deleted tenant")

    delete_selected.short_description = "Delete selected"
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj=obj)
        return fields
    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                ('Thông tin chung', {
                'fields': ('site_name', 'phone', 'site_image','service_package', 'type', 'is_active', 'on_trial', 'is_template','is_default', 'schema_name', 'theme_folder','paid_until', 'allow_sale_via_bank', 'allow_sync_appsim', 'allow_adjust_price_for_khosim', 'allow_adjust_price_for_appsim')
                }), )
        return (
                ('Thông tin chung', {
                'fields': ('site_name','phone', 'site_image', 'user',"service_package", "type", 'is_active', 'on_trial', 'is_template', 'is_default')
                }), )
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('schema_name', 'dns_record', 'theme_folder')
        return self.readonly_fields
    def get_exclude(self, request, obj=None):
        # Specify fields to exclude when creating
        if obj:
            return self.exclude
        return self.exclude + ('theme_folder',)
    def save_model(self, request, obj, form, change):
        if not change:
            # Clone the existing tenant
            print(form)
            uuid_str = str(uuid.uuid4())
            uuid_str = uuid_str[:8]
            tenant_type = form.cleaned_data.get('type')
            source_tenant = Tenant.objects.filter(type=tenant_type, is_template=True, is_default=True).first()
            obj.schema_name = f'{source_tenant.type}_{uuid_str}'
            source_tenant.clone_schema(obj.schema_name)
            obj.theme_config = source_tenant.theme_config
            obj.config = source_tenant.config
            obj.type = source_tenant.type
            obj.dns_record = uuid.uuid4()
            obj.is_template = False
            obj.is_default = False
            obj.theme_folder = source_tenant.theme_folder
            obj.paid_until = datetime.now().date() + timedelta(days=15)
        else:
            allow_sale_via_bank = form.cleaned_data.get('allow_sale_via_bank')
            allow_sync_appsim = form.cleaned_data.get('allow_sync_appsim')
            allow_adjust_price_for_khosim = form.cleaned_data.get('allow_adjust_price_for_khosim')
            allow_adjust_price_for_appsim = form.cleaned_data.get('allow_adjust_price_for_appsim')
            if allow_sale_via_bank:
                # neu ton tai allow_sale_via_bank va true thi tenant mơi hiển thị config này
                obj.config['allow_sale_via_bank'] = allow_sale_via_bank
            elif 'allow_sale_via_bank' in obj.config:
                del obj.config['allow_sale_via_bank']

            if allow_sync_appsim:
                obj.config['allow_sync_appsim'] = allow_sync_appsim
            elif 'allow_sync_appsim' in obj.config:
                del obj.config['allow_sync_appsim']
                
            if allow_adjust_price_for_khosim:
                obj.config['allow_adjust_price_for_khosim'] = allow_adjust_price_for_khosim
            elif 'allow_adjust_price_for_khosim' in obj.config:
                del obj.config['allow_adjust_price_for_khosim']
            
            if allow_adjust_price_for_appsim:
                obj.config['allow_adjust_price_for_appsim'] = allow_adjust_price_for_appsim
            elif 'allow_adjust_price_for_appsim' in obj.config:
                del obj.config['allow_adjust_price_for_appsim']
        super().save_model(request, obj, form, change)

admin.site.unregister(Tenant)
admin.site.register(Tenant, TenantAdminOverrideAdmin)

@admin.register(TenantTemplates)
class TenantTemplateAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'tenant_type', 'description', 'featured_img')
    exclude = ['createdAt', 'updatedAt']
    # gen slug by name
    prepopulated_fields = {'slug': ('name',), }

    def _only_public_tenant_access(self, request):
        try:
            return True if request.tenant.schema_name == get_public_schema_name() else False
        except AttributeError:
            return True
        
    def has_view_permission(self, request, view=None):
        return self._only_public_tenant_access(request)

    def has_add_permission(self, request, view=None):
        return self._only_public_tenant_access(request)
    
    def has_change_permission(self, request, view=None):
        return self._only_public_tenant_access(request)

    def has_delete_permission(self, request, view=None):
        return self._only_public_tenant_access(request)

    def has_view_or_change_permission(self, request, view=None):
        return self._only_public_tenant_access(request)
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
