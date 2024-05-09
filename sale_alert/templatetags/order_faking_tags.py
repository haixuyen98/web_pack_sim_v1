
from django.template import Library

register = Library()

@register.filter
def render_top10_order_faking(tenant, prefix):
    tenant_id = tenant.schema_name
    return f'{prefix}:{tenant_id}'
