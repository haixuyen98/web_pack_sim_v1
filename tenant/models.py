from django.db import models
from django.contrib.auth.models import User
from django_tenants.models import DomainMixin, TenantMixin
from django.db import connection
from django_tenants.utils import get_tenant_types
from tenant.helpers import reset_sequences
from tenant.constants import SERVICE_PACKAGES

def theme_config_default():
    return {}
def other_config_default():
    return {}
class Tenant(TenantMixin):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    site_name = models.CharField(max_length=50, verbose_name='Tên site (*)')
    site_image = models.ImageField(null=True, blank=True, upload_to="profile")
    type = models.CharField(max_length=100, choices=[], default='', verbose_name="Loại hình kinh doanh (*)")
    service_package = models.IntegerField(choices=SERVICE_PACKAGES.choices, default=SERVICE_PACKAGES.BASIC, verbose_name="Gói dịch vụ")
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name='Số điện thoại (*)')

    # featured = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    # default galaxy, is theme folder name in templates folder
    theme_folder = models.CharField(max_length=50, default='galaxy')
    dns_record = models.CharField(max_length=50, default='')
    theme_config = models.JSONField("ThemeConfig", default=theme_config_default)
    config = models.JSONField("TenantConfig", default=other_config_default)
    paid_until = models.DateField(auto_now_add=False, null=False)
    on_trial = models.BooleanField(default=True)
    is_template = models.BooleanField(default=True,blank=False,null=False)
    is_default = models.BooleanField(default=True,blank=False,null=False)
    # default true, schema will be automatically created and
    # synced when it is saved
    auto_create_schema = True

    """
    USE THIS WITH CAUTION!
    Set this flag to true on a parent class if you want the schema to be
    automatically deleted if the tenant row gets deleted.
    """
    auto_drop_schema = True


    class Meta:
        ordering = ('-updated_at',)

    def __init__(self, *args, **kwargs):
        super(Tenant, self).__init__(*args, **kwargs)
        # Dynamically initialize choices for the field
        tenant_types = get_tenant_types()
        tenant_types = [(key, value['label']) for key, value in tenant_types.items() if key != 'public' and 'label' in value]
        self._meta.get_field('type').choices = tenant_types
    def __str__(self):
        return f"{self.site_name}"

    def clone_schema(self, target_schema):
        source_schema = self.schema_name
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT public.clone_schema('{source_schema}', '{target_schema}', true, false)")
        reset_sequences(target_schema)
class TenantTemplates(models.Model):
    
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, max_length=10)
    link = models.CharField(null=True, max_length=200)
    theme_config_url = models.CharField(null=True, max_length=200)
    tenant_type = models.CharField(max_length=40, choices=[])
    description = models.TextField(null=True, blank=True, max_length=170)
    featured_img = models.ImageField(null=True, blank=True,upload_to='')
    timestamp = models.DateTimeField(auto_now_add=True)
    publishedAt = models.DateField(auto_now_add=True)
    class Meta:
        verbose_name = "Tenant Templates"
        verbose_name_plural = "Tenant Templates"
        db_table = "tenant_templates"
    
    def __str__(self):
        return self.name
    def __init__(self, *args, **kwargs):
        super(TenantTemplates, self).__init__(*args, **kwargs)
        # Dynamically initialize choices for the field
        tenant_types = get_tenant_types()
        tenant_types = [(key, value['label']) for key, value in tenant_types.items() if key != 'public' and 'label' in value]
        self._meta.get_field('tenant_type').choices = tenant_types

class Domain(DomainMixin):
    pass
