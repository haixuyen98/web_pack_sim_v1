from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from core.helpers import get_content_type
from .models import SeoFile
from django.http import Http404
from sims.services.helpers import parse_content
import html

# Create your views here.
def seo_file_view(request, path):
    context = {
        'request': request    
    }
    record = get_object_or_404(SeoFile, name=path)
    if record:
        content = parse_content("{% load core_tags %} {% get_current_base_url as base_url %}" + html.unescape(record.content), context)
        content_type = get_content_type(path)
        return HttpResponse(content, content_type=content_type)
    raise Http404("Page not found")
