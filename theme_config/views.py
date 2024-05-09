from django_tenants.utils import remove_www
from tenant.models import Domain
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from core.helpers import uploadFileTenant
from theme_config.apps import ThemeConfig
from core.helpers import autoClearCache

# Create your views here.
@login_required
def index(request):
    tenant = request.tenant
    hostname_without_port = remove_www(request.get_host().split(':')[0]) 
    domain = Domain.objects.get(domain=hostname_without_port)
    # name = domain.tenant.site_name
    context = {
        'home_page_url': domain.domain,
        'tenant': tenant,
        'theme_color_templates': ThemeConfig.theme_color_templates,
        'font_family_templates': ThemeConfig.font_family_templates,
    }
    return render(request, f'admin/{tenant.type}/theme-config.html', context)

def saveTheme(request):
    # hostname_without_port = remove_www(request.get_host().split(':')[0]) 
    # domain = Domain.objects.get(domain=hostname_without_port)
    tenant = request.tenant
    if request.method == 'POST':
        # demo update sample data
        if request.POST.get('resetTheme') == 'true':
            tenant.theme_config = ThemeConfig.theme_config_default
            tenant.save()
        else:
            site_image_path = request.POST.get('site_image_path')
            site_image_file = request.FILES.get('site_image')

            if site_image_file:
                uploaded_file_url = uploadFileTenant(site_image_file)
                if uploaded_file_url:
                    tenant.site_image = uploaded_file_url
            elif site_image_path == '' or site_image_path is None:
                tenant.site_image = '/static/galaxy/images/default.jpg'

            favicon_path = request.POST.get('favicon_path')
            favicon_file = request.FILES.get('favicon')
            if not hasattr(tenant.theme_config, 'seo'):
                tenant.theme_config["seo"] = {}
            if favicon_file:
                uploaded_file_favicon_url = uploadFileTenant(favicon_file)
                if uploaded_file_favicon_url:
                    tenant.theme_config["seo"]['favicon'] = uploaded_file_favicon_url
            elif favicon_path == '' or favicon_path is None:
                tenant.theme_config["seo"]['favicon'] = '/static/galaxy/images/default.jpg'
            tenant.site_name= request.POST.get('site_name')
            # tenant.theme_config["email"] = "mun@gmail.com"
            tenant.theme_config["menu_top"] = eval(request.POST.get('menu_top'))
            tenant.theme_config["sidebar"] = eval(request.POST.get('sidebar'))
            tenant.theme_config["support"] = {
                'title1': request.POST.get('title1'),
                'hotline1': request.POST.get('hotline1'),
                'title2': request.POST.get('title2'), 
                'hotline2': request.POST.get('hotline2'), 
                'facebook': request.POST.get('facebook'),
                'messenger': request.POST.get('messenger'),
                'linkedin': request.POST.get('linkedin'),
                'twitter': request.POST.get('twitter'),
                'youtube': request.POST.get('youtube'),
                'zalo': request.POST.get('zalo'),
                'business_hours': request.POST.get('business_hours'),
                'email': request.POST.get('email'),
                'download_and_certification': request.POST.get('download_and_certification'),
                'displayStyle': request.POST.get('displayStyle'),
            }
            tenant.theme_config["seo"]['description'] = request.POST.get('description')
            tenant.theme_config["seo"]['headScript'] = request.POST.get('headScript')
            tenant.theme_config["seo"]['footerScript'] = request.POST.get('footerScript')
            tenant.theme_config["footer_link"] = eval(request.POST.get('footer_link'))
            tenant.theme_config["color"] = {
                'main_color': request.POST.get('main_color'), 
                'second_color': request.POST.get('second_color'),
                'color_bg': request.POST.get('color_bg'), 
                'text_color': request.POST.get('text_color'),
                'text_highlight': request.POST.get('text_highlight'),
                'color_bg_menu': request.POST.get('color_bg_menu'),
                'color_text_menu': request.POST.get('color_text_menu'),
                'font_family': request.POST.get('font_family'),
                'font_size': request.POST.get('font_size'),
            }

            # Banner1
            banner1_path = request.POST.get('banner1_path')
            banner1_file = request.FILES.get('banner1')

            uploaded_file_url1 = None
            if banner1_file:
                uploaded_file_url1 = uploadFileTenant(banner1_file)

            # Banner2
            banner2_path = request.POST.get('banner2_path')
            banner2_file = request.FILES.get('banner2')

            uploaded_file_url2 = None
            if banner2_file:
                uploaded_file_url2 = uploadFileTenant(banner2_file)

            # Banner3
            banner3_path = request.POST.get('banner3_path')
            banner3_file = request.FILES.get('banner3')

            uploaded_file_url3 = None
            if banner3_file:
                uploaded_file_url3 = uploadFileTenant(banner3_file)

            tenant.theme_config["banner"] = {
                'banner1': uploaded_file_url1 if uploaded_file_url1 else (banner1_path if banner1_path else '/static/galaxy/images/default.jpg'),
                'url_banner1': request.POST.get('url_banner1'),
                'title_banner1': request.POST.get('title_banner1'),
                'banner2': uploaded_file_url2 if uploaded_file_url2 else (banner2_path if banner2_path else '/static/galaxy/images/default.jpg'),
                'url_banner2': request.POST.get('url_banner2'),
                'title_banner2': request.POST.get('title_banner2'),
                'banner3': uploaded_file_url3 if uploaded_file_url3 else (banner3_path if banner3_path else '/static/galaxy/images/default.jpg'),
                'url_banner3': request.POST.get('url_banner3'),
                'title_banner3': request.POST.get('title_banner3'),
            }
         # tenant.theme_config["sidebar"] = [{"title": "SIM THEO GIÁ", "content": "{% sidebar_prices_block 'SIM THEO GIÁ' %}"}, {"title": "SIM THEO NHÀ MẠNG", "content": "{% sidebar_telco_block %}"}, {"title": "SIM THEO MỆNH", "content": "{% sidebar_fates_block 'SIM THEO MỆNH'%}"}, {"title": "LOẠI SIM", "content": "{% sidebar_types_block 'LOẠI SIM'%}"}, {"title": "TỪ KHOÁ PHỔ BIẾN", "content": "{% sidebar_tags_block 'TỪ KHOÁ PHỔ BIẾN'%}"}]
            autoClearCache(request)
            tenant.save()
    return redirect(
        f'{reverse("theme_config:config_index", args=[])}'
    )