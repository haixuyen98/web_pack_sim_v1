from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django_tenants.utils import get_tenant_types
from core.helpers import get_current_tenant
from . import views

handler404 = views.custom_404
handler500 = views.custom_500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('clear/', views.clear_cache, name='core_clear_ache'),
]
from core.helpers import get_current_tenant

# dynamic regiter module urls
tenant_types = get_tenant_types()
tenant = get_current_tenant()
type = tenant_types.get(tenant.type)
urlpatterns_app = type['urlpatterns_app'] if 'urlpatterns_app' in type else []
for item in urlpatterns_app:
    urlpatterns.append(path('', include(item[0]), name=item[1]))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
admin.site.index_title="WELCOME TO ADMINISTRATOR"
admin.site.site_header="WEBSITE ADMINISTRATOR"
admin.site.site_title = "ADMINISTRATOR SITE"