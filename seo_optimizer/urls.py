from django.urls import re_path, path
from . import views
from django.contrib.sitemaps.views import sitemap

from blog.sitemaps import ArticleSitemap #import ArticleSitemap

sitemaps = {
    'blog':ArticleSitemap #add DynamicSitemap to the dictionary
}

urlpatterns = [
    path('tin-tuc/sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^(?P<path>[a-zA-Z0-9_-]+\.[a-z]{3,10})$', views.seo_file_view, name='seo_file_view'),
]
