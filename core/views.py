from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.shortcuts import render
from .helpers import autoClearCache

@login_required
@never_cache
def clear_cache(request):
    autoClearCache(request)
    data = {
        'status': 'OK',
        'message': 'Clear redis cache successful!',
    }
    return JsonResponse(data)


def custom_404(request, exception=None):
    tenant = request.tenant
    return render(request, f'{tenant.theme_folder}/404.html', status=404)

def custom_500(request, exception=None):
    tenant = request.tenant
    return render(request, f'{tenant.theme_folder}/500.html', status=500)