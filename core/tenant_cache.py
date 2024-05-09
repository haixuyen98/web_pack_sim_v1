from django_redis.cache import RedisCache
from core.helpers import get_current_tenant

class TenantRedisCache(RedisCache):
    def make_key(self, key, version=None, prefix=None):
        # Retrieve the tenant-specific prefix from the request or any other appropriate source
        current_tenant = get_current_tenant()
        tenant_prefix= "public"
        if current_tenant:
            tenant_prefix = current_tenant.schema_name
        full_key = super().make_key(key, version=version, prefix=prefix)
        return f"{tenant_prefix}:{full_key}"
    # def __init__(self, location, params):
    #     current_tenant = get_current_tenant()
    #     if current_tenant:
    #         location = f'{current_tenant.schema_name}-{location}'
    #     super().__init__(location, params)
