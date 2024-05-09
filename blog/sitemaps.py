from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article

class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    protocol = 'https'
 
    def items(self):
        return Article.postManager.all()
    
    def lastmod(self, obj):
        return obj.publishedAt
    
    def location(self, obj):
        return '/tin-tuc/%s' % (obj.slug)

