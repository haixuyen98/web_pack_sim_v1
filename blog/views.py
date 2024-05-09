from django.shortcuts import render, get_object_or_404
from .models import Article, Profile, Category
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from sims.services.helpers import getSeo, parse_content
from django.views.decorators.cache import cache_page
import html
import bleach
from django.contrib.auth.models import User

@cache_page(60 * 15)
def articles(request):
    tenant = request.tenant
    LIMIT = 15
    query = request.GET.get('query')
    if query == None:
        query = ''

    articles_list = Article.postManager.filter(Q(title__icontains=query) | Q(excerpt__icontains=query))
    articles_length = articles_list.count()
    meta_data = {'total': articles_length, 'page': 1, 'limit': LIMIT}
    paginator = Paginator(articles_list, LIMIT) 
    page_number = int(request.GET.get('p', 1))
    articles = paginator.get_page(page_number)
    breadcrumb_data = [
        {'title': 'Trang chủ', 'href': '/'},
        {'title': 'Tin tức', 'href': ''},
    ]

    context = {
        'articles': articles,
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'meta_data': meta_data,
        'tenant': tenant,
        'breadcrumb_data': breadcrumb_data,
        'query': query
    }
    context['seo'] = getSeo(articles_list, tenant, context)
    return render(request, f'{tenant.theme_folder}/blog/articles.html', context)

@cache_page(60 * 15)
def byCategory(request, slug):
    tenant = request.tenant
    LIMIT = 15
    query = request.GET.get('query')
    if query == None:
        query = ''
    category_name = get_object_or_404(Category, slug=slug)

    articles_list = Article.postManager.filter(
        Q(title__icontains=query, category=category_name) |
        Q(excerpt__icontains=query, category=category_name)
    )
    articles_length = articles_list.count()
    meta_data = {'total': articles_length, 'page': 1, 'limit': LIMIT}
    paginator = Paginator(articles_list, LIMIT) 
    page_number = int(request.GET.get('p', 1))
    articles = paginator.get_page(page_number)
    breadcrumb_data = [
        {'title': 'Trang chủ', 'href': '/'},
        {'title': 'Tin tức', 'href': '/tin-tuc/'},
        {'title': category_name, 'href': ''},
    ]

    context = {
        'articles': articles,
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'meta_data': meta_data,
        'tenant': tenant,
        'name_content': category_name,
        'breadcrumb_data': breadcrumb_data
    }
    context['seo'] = getSeo(articles_list, tenant, context)
    return render(request, f'{tenant.theme_folder}/blog/category.html', context)

@cache_page(60 * 15)
def byAuthor(request, author):
    tenant = request.tenant
    LIMIT = 15
    query = request.GET.get('query')
    if query == None:
        query = ''
    author_name = get_object_or_404(User, username=author)

    # Assuming 'Article' model has a ForeignKey or OneToOneField named 'author' linking to 'Profile'
    articles_list = Article.postManager.filter(
        Q(title__icontains=query, user=author_name) |
        Q(excerpt__icontains=query, user=author_name)
    )

    articles_length = articles_list.count()
    meta_data = {'total': articles_length, 'page': 1, 'limit': LIMIT}
    paginator = Paginator(articles_list, LIMIT) 
    page_number = int(request.GET.get('p', 1))
    articles = paginator.get_page(page_number)
    breadcrumb_data = [
        {'title': 'Trang chủ', 'href': '/'},
        {'title': 'Tin tức', 'href': '/tin-tuc/'},
        {'title': author_name, 'href': ''},
    ]

    context = {
        'articles': articles,
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'meta_data': meta_data,
        'tenant': tenant,
        'name_content': author_name,
        'breadcrumb_data': breadcrumb_data
    }
    context['seo'] = getSeo(articles_list, tenant, context)
    return render(request, f'{tenant.theme_folder}/blog/author.html', context)

@cache_page(60 * 15)
def article(request, article):
    tenant = request.tenant
    host = request.get_host()
    article = get_object_or_404(Article, slug=article, status=Article.StatusType.PUBLISHED)
    breadcrumb_data = [
        {'title': 'Trang chủ', 'href': '/'},
    ]
    if article.category:
        breadcrumb_data.append({'title': article.category, 'href': f'/tin-tuc/c/{article.category.slug}'})
    else:
        breadcrumb_data.append({'title': 'Tin tức', 'href': '/tin-tuc/'})
    breadcrumb_data.append({'title': article.title, 'href': ''})

    # Related articles
    related_articles = Article.postManager.filter(
        Q(category=article.category),
    ).exclude(id=article.id)[:5]
    
    context = {
        'article': article,
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'host': host,
        'tenant': tenant,
        'breadcrumb_data': breadcrumb_data
    }
    if article.category:
        context['related_articles'] = related_articles

    context['content'] = parse_content(html.unescape(article.body), context)
    context['seo'] = getSeo(article, tenant, context)
    context['title'] = parse_content(html.unescape(article.title), context)
    context['clean_html'] = bleach.clean(
        article.body,
        tags=[ "amp-img", "p", "div", "a", "h2", "h3", "h4", "span", "strong", "nav", "ul", "li", "img" ],
        attributes={ "amp-img": ["src", "width", "height", "layout", "alt"], "div": ["id", "class"], "span": ["style", "id"], "a": ["href"], "img": ["alt", "src", "style"] },
        strip=True
    )
    breadcrumb_data[-1]['title'] = context['title']
    if request.path.endswith('amp/'):
        return render(request, f'{tenant.theme_folder}/blog/article_amp.html', context)
    else:
        return render(request, f'{tenant.theme_folder}/blog/article.html', context)

def page404(request, article):
    tenant = request.tenant
    article = get_object_or_404(Article, slug=article, status=Article.StatusType.PUBLISHED)
    context = {
        'article': article,
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
    }
    return render(request,  f'{tenant.theme_folder}/blog/article.html', context)


def genRobotFile(request):
    tenant = request.tenant
    robots = tenant.config['robots']
    return HttpResponse(robots, content_type="text/plain")