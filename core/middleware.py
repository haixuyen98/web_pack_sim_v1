from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import remove_www_and_dev, get_public_schema_urlconf    
from django.http import HttpResponse
import dns.resolver
from django.http import HttpResponseForbidden
from django.utils import timezone
import os

class CustomException(Exception):
    pass


class TenantMiddleware(TenantMainMiddleware):
    """
    Field is_active can be used to temporary disable tenant and
    block access to their site. Modifying get_tenant method from
    TenantMiddleware allows us to check if tenant should be available
    """

    def get_tenant(self, domain_model, hostname):
        tenant = super().get_tenant(domain_model, hostname)
        return tenant 
   
    # def no_tenant_found(self, request, hostname):
    #     hostname_without_port = remove_www_and_dev(request.get_host().split(':')[0])

    #     if hostname_without_port in (os.environ.get('WHITE_LIST_DOMAIN', '').split(",")):
    #         request.urlconf = get_public_schema_urlconf()
    #         return
    #     else:
    #         raise self.TENANT_NOT_FOUND_EXCEPTION('No tenant1 for hostname "%s"' % hostname)

class HealthCheckMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/health':
            return HttpResponse('ok')
        return self.get_response(request)


class DNSResolverMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        hostname_without_port = remove_www_and_dev(request.get_host().split(':')[0])
        # bypass localhost
        if "127.0.0.1" in hostname_without_port or "localhost" in hostname_without_port or '10.244.1.14' in hostname_without_port:
            return self.get_response(request)
        try:
            answers = dns.resolver.resolve("aaa.asdflkjsadf.websim.vn", 'TXT')
            valid = False
            for record_value in answers:
                if record_value == request.tenant.dns_record:
                    valid = True
            if not valid:
                return HttpResponse('This domain not yet add TXT record1.')
            return self.get_response(request)
        except dns.resolver.NXDOMAIN:
            return HttpResponse('This domain not yet add TXT record2.')
        except dns.resolver.Timeout:
            return HttpResponse('This domain not yet add TXT record3.')
        except dns.exception.DNSException:
            return HttpResponse('This domain not yet add TXT record4.')

class InactiveTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is associated with a tenant
        # if not hasattr(request, 'tenant'):
        #     return HttpResponseForbidden('Your Tenant is not found. Please contact with administrator.')
        if hasattr(request, 'tenant') and not request.tenant.is_active:
            return HttpResponseForbidden('Your Tenant is inactive. Please contact with administrator.')
        if hasattr(request, 'tenant') and request.tenant.paid_until and  request.tenant.paid_until < timezone.now().date():
            return HttpResponseForbidden('Your Tenant is expired (paid until). Please contact with administrator.')
        return self.get_response(request)
class DisableCSRFMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)
        response = self.get_response(request)
        return response
