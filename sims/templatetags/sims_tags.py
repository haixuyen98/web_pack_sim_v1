from django.template import Library, loader, Context, Template
from sims.services.sim_service import getSims
from urllib.parse import parse_qsl
from sims.apps import SimsConfig
import json
from sims.services.helpers import getSimUrlFilter, convertArrayLogobyTheme
import math
import html
from sims.services.helpers import vn_date_format
import re
from urllib.parse import urlparse, urlencode
from blog.models import ArticlePage
import math
import datetime

register = Library()

@register.simple_tag(takes_context=True)
def sim_block(context, title, query_str, link_more):
    theme_folder = context["theme_folder"]
    tenant = context["tenant"]
    params = dict(parse_qsl(query_str))
    response_data = getSims(params, tenant, None)
    listSim = response_data['data'] if 'data' in response_data else []
    t = loader.get_template(f'{theme_folder}/sims/sim-block.html')
    return t.render({
        'listSim': listSim,
        'title': title,
        'link_more': link_more,
        'theme_folder': theme_folder
    })

@register.simple_tag(takes_context=True)
def sim_installment_block(context, title, query_str, link_more):
    theme_folder = context["theme_folder"]
    tenant = context["tenant"]
    params = dict(parse_qsl(query_str))
    page = ArticlePage.pageManager.filter(slug="sim-tra-gop").first()
    if page:
        store_type = page.store_config.get('store_type', None)
        params['store_type'] = store_type
    response_data = getSims(params, tenant, None)
    listSim = response_data['data'] if 'data' in response_data else []
    t = loader.get_template(f'{theme_folder}/sims/sim-block.html')
    return t.render({
        'listSim': listSim,
        'title': title,
        'link_more': link_more,
        'theme_folder': theme_folder
    })

@register.simple_tag(takes_context=True)
def filter_prices_block(context, title):
    theme_folder = context["theme_folder"]
    t = loader.get_template(f'{theme_folder}/layout/components/sidebar_filter_prices.html')
    return t.render({
        'items': SimsConfig.filterPrice,
        'title': title
    })

    
@register.simple_tag(takes_context=True)
def filter_telco_head_block(context, title):
    theme_folder = context["theme_folder"]
    t = loader.get_template(f'{theme_folder}/layout/sim-block.html')
    return t.render({
        'items': SimsConfig.filterTel,
        'title': title
    })


@register.simple_tag(takes_context=True)
def showFilterAdv(context, hide_sort=1):
    theme_folder = context["theme_folder"]
    t = loader.get_template(f'{theme_folder}/sims/search/filter-adv.html')
    request = context['request']
    paramsObj = request.GET.dict()
    filterObj = getSimUrlFilter(request.path, paramsObj)
    modified_filterTel = convertArrayLogobyTheme(SimsConfig.filterTel, theme_folder)
    modified_filterFates = convertArrayLogobyTheme(SimsConfig.filterFates, theme_folder)
    
    return t.render({
        'filterPrice': json.dumps(SimsConfig.filterPrice),
        'filterTel': json.dumps(modified_filterTel),
        'filterFates': json.dumps(modified_filterFates),
        'filterTypes': SimsConfig.filterTypes,
        'filterHead': SimsConfig.filterHead,
        'filterObj': filterObj,
        'hide_sort': hide_sort
    })


@register.filter
def renderLogoTelIcon(theme_folder, value):
    logoTel = ''
    for dataItem in SimsConfig.filterTel:
       if dataItem['telco'] == value:
           logoTel = dataItem['logo'].format(theme_folder=theme_folder)
    return logoTel


@register.filter
def parserHtmlToPY(htmlString):
  if htmlString:
    template = Template(htmlString)
    context = Context({})
    reactElement = template.render(context)
    return reactElement
  else:
    return ""


@register.filter
def formatPrice(num):
    try:
        num = float(num)
    except (ValueError, TypeError):
        return "0"
    priceWithComma = "{:,.0f} ₫".format(num)
    priceWithDot = priceWithComma.replace(',', '.')
    return priceWithDot

@register.filter
def sub(value, arg):
    return value - arg

@register.filter
def get_value_from_key(options, key):
    if options:
        if key in options:
            return options[key]
        else:
            return None
    else:
        return None
    
@register.filter
def get_record_from_array(data_array, target_id):
    found_record = None
    if data_array:
        for record in data_array:
            if record.get('id') == int(target_id):
                found_record = record
                break
        return found_record
    else:
        return None
@register.filter
def get_max_from_array(options, key):
    if options and key in options and options[key]:
        return max(options[key], key=lambda x: x["pi"])["pi"]
    else:
        return None

@register.filter
def removeDot(sdt):
    return sdt.replace(".", "")

@register.filter
def parseSideBarItem(value, theme_folder):
    t = Template(html.unescape("{% load sims_tags %} " + value))
    return t.render(Context({'theme_folder': theme_folder, 'title': ''}))

@register.filter
def date_format(value):
    return vn_date_format(value)

@register.filter(name='replace_tenant_site_name')
def replace_tenant_site_name(value, tenant):
    tenant_site_name = tenant.site_name
    tenant_phone = tenant.phone
    if tenant_site_name is None:
        tenant_site_name = ""
    if tenant_phone is None:
        tenant_phone = ""
    value_with_site_name = value.replace('{{tenant.site_name}}', tenant_site_name)
    return value_with_site_name.replace('{{tenant.phone}}', tenant_phone)

@register.simple_tag(takes_context=True)
def add_page_param(context, page_num):
    request = context['request']
    params = request.GET.copy()
    params['p'] = page_num  # Thêm hoặc cập nhật tham số 'p' với giá trị là page_num
    new_url = request.path + '?' + urlencode(params)
    return new_url

@register.simple_tag(takes_context=True)
def sidebar_prices_block(context, title=None):
    theme_folder = context["theme_folder"]
    title = context['title'] if context['title'] is not None else title
    t = loader.get_template(f'{theme_folder}/layout/components/sidebar_filter_prices.html')
    return t.render({
        'items': SimsConfig.filterPrice,
        'title': title
    })


@register.simple_tag(takes_context=True)
def sidebar_fates_block(context, title=None):
    theme_folder = context["theme_folder"]
    title = context['title'] if context['title'] is not None else title
    modified_filterFates = convertArrayLogobyTheme(SimsConfig.filterFates, theme_folder)
    t = loader.get_template(f'{theme_folder}/layout/components/sidebar_filter_fates.html')
    return t.render({
        'items': modified_filterFates,
        'title': title
    })


@register.simple_tag(takes_context=True)
def sidebar_types_block(context, title=None):
    theme_folder = context["theme_folder"]
    title = context['title'] if context['title'] is not None else title
    t = loader.get_template(f'{theme_folder}/layout/components/sidebar_filter_types.html')
    return t.render({
        'filterTypes': SimsConfig.filterTypes,
        'title': title
    })


@register.simple_tag(takes_context=True)
def sidebar_tags_block(context, title=None):
    theme_folder = context["theme_folder"]
    title = context['title'] if context['title'] is not None else title
    t = loader.get_template(f'{theme_folder}/layout/components/sidebar_filter_tags.html')
    return t.render({
        'items': SimsConfig.filterPopularKeyword,
        'title': title
    })


@register.simple_tag(takes_context=True)
def sidebar_telco_block(context, title=None):
    theme_folder = context["theme_folder"]
    title = context['title'] if context['title'] is not None else title
    modified_filterTel = convertArrayLogobyTheme(SimsConfig.filterTel, theme_folder)
    t = loader.get_template(f'{theme_folder}/layout/components/sidebar_filter_telco.html')
    return t.render({
        'numbers': SimsConfig.filterHead,
        'images': modified_filterTel,
        'title': title
    })


@register.simple_tag(takes_context=True)
def banner_slide(context):
    theme_folder = context.get("theme_folder")
    banners = context.get("theme_config").get("banner", None)
    banner = {}
    if banners:
        banner1 = tuple([banners[item] for item in ['banner1', 'url_banner1', 'title_banner1'] if banners.get(item)])
        banner2 = tuple([banners[item] for item in ['banner2', 'url_banner2', 'title_banner2'] if banners.get(item)])
        banner3 = tuple([banners[item] for item in ['banner3', 'url_banner3', 'title_banner3'] if banners.get(item)])
        banner = {
            banner1: banner1,
            banner2: banner2,
            banner3: banner3,
        }
        t = loader.get_template(f'{theme_folder}/layout/components/banner_slide.html')
        if len(banner) > 0:
            return t.render({
                'urls': banner,
                'rangeAmount': range(len(banner)),
            })
    return ''


@register.simple_tag(takes_context=True)
def pagination(context):
    theme_folder = context["theme_folder"]
    meta_data = context['meta_data']
    request = context['request']
    total_sim = meta_data.get("total", 0)
    limit = int(meta_data.get("limit", '60'))
    total_pages = math.ceil(total_sim / limit)
    current = int(request.GET.get('p', 1))

    start = max(1, current - 2)
    end = min(total_pages, start + 4)

    if current > total_pages - 2:
        start = max(1, total_pages - 4)
        end = total_pages

    pages = list(range(start, end + 1))

    prev_page = current - 1 if current > 1 else None
    next_page = current + 1 if current < total_pages else None

    t = loader.get_template(f'{theme_folder}/sims/pagination.html')
    return t.render({
        'request': request,
        'current': current,
        'prev_page': prev_page,
        'next_page': next_page,
        'pages': pages,
        'total_pages': total_pages,
    })

@register.simple_tag(takes_context=True)
def filter_year_birth(context, title):
    theme_folder = context["theme_folder"]
    t = loader.get_template(f'{theme_folder}/layout/components/filter_year_birth.html')
    return t.render({
        'items': SimsConfig.filterYearBirth,
        'title': title
    })

@register.filter
def removeSingleQuote(sdt):
    return sdt.replace('"', "")

@register.filter
def find_img_url(value):
    # Sử dụng regular expression để tìm URL của ảnh đầu tiên trong nội dung HTML
    match = re.search(r'<img.*?src=["\'](.*?)["\']', value)
    if match:
        return match.group(1)
    return None

@register.filter
def getDomain(value):
    parsed_url = urlparse(value)
    domain = parsed_url.netloc
    return domain

@register.filter
def format_tra_gop(price):
    giasim = float(price)
    phantramvay = 30
    monthTragop = 12
    tongtientamtinh = (giasim * phantramvay) / 100
    sotienno = giasim - tongtientamtinh
    tongtienmoithangtamtinh = (sotienno / monthTragop) * (1 + ((monthTragop + 1) * 0.03) / 2)
    lamtrontongtien = math.ceil(tongtienmoithangtamtinh / 1000) * 1000
    formatted_price = "{:,.0f}".format(lamtrontongtien)
    formatted_price = formatted_price.replace(",", ".")
    formatted_price = formatted_price[:-4]
    return "Góp {}k/th".format(formatted_price)

@register.filter
def format_date(date_str):
    if date_str:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d-%m-%Y')
        return formatted_date

@register.filter
def format_menh_chu(menh_chu):
    formatted_menh_chu = '<br>'.join(menh_chu)
    return formatted_menh_chu

@register.filter
def render_price(price):
    new_price = round(float(price))
    formatted_price = f"{new_price:,.0f} ₫"
    return formatted_price
