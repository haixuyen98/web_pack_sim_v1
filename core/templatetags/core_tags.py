
from django.template import Library

register = Library()

@register.filter
def tenant_cache_key(tenant, prefix):
    tenant_id = tenant.schema_name
    return f'{prefix}_{tenant_id}'

@register.simple_tag(takes_context=True)
def get_current_base_url(context):
    request = context['request']
    base_url = request.build_absolute_uri('/')[:-1]

    # Construct the base URL using the request's scheme and host
    # base_url = request.scheme + '://' + request.get_host() + "/"

    return base_url