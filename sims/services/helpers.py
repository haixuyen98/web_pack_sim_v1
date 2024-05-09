import urllib.parse
from sims.apps import SimsConfig
import re
from django.utils import timezone
from datetime import datetime
from pytz import timezone as pytz_timezone
from django.template import Template, Context
import html
from urllib.parse import parse_qs
from sims.common.choices import CATEGORY_CHOICES, get_label_from_value
from sims.common.choices import NHA_MANG_CHOICES
from datetime import timedelta

def url_params_to_obj(params_str):
    res = urllib.parse.parse_qs(params_str)
    return res

def getSimUrlFilter(url_path, paramsObj, page=None):
    # remove slash in last charector
    if url_path[-1] == '/':
        url_path = url_path[:-1]
    filter = None
    # neu trong paramsObject co đối số q thì xử lý search theo q trước, các phàn sau sẽ override nếu có
    if 'q' in paramsObj and len(paramsObj['q'])>0:
        filter = keyword_to_object_params(paramsObj['q'])
        filter['title'] = f"Kết quả tìm kiếm {paramsObj['q']}"
    # sim dau so
    x = re.search("sim-dau-so-(\d{1,})", url_path)
    if x:
        for item in SimsConfig.filterHead:
            if item['link'] == url_path or item['link'] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['h'] = x.group(1)
            filter['title'] = f"Sim đầu số {x.group(1)}"
            return {**filter, **paramsObj}
    x = re.search("sim-tien-len-dau-(\d{2,})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['h'] = x.group(1)
            filter['title'] = f"{filter['title']} đầu {filter['h']}"
            return {**filter, **paramsObj}
    x = re.search("sim-tien-len-duoi-(\d{2,})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['title'] = f"{filter['title']} đuôi {filter['tail']}"
            return {**filter, **paramsObj}
    x = re.search("sim-tien-len-duoi-(\d{2,})-dau-(\d{2,})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['h'] = x.group(2)
            filter['title'] = f"{filter['title']} đuôi {filter['tail']} đầu {filter['h']}"
            return {**filter, **paramsObj}
    # sim tu quy
    x = re.search("sim-ngu-quy-(\d{5})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['title'] = f"{filter['title']} {filter['tail']}"
            return {**filter, **paramsObj}
    x = re.search("sim-ngu-quy-(\d{5})-dau-(\d{2,3})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['h'] = x.group(2)
            filter['title'] = f"{filter['title']} {filter['tail']} đầu {x.group(2)}"
            return {**filter, **paramsObj}
    x = re.search("sim-ngu-quy-dau-(\d{2,4})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['h'] = x.group(1)
            filter['title'] = f"{filter['title']} đầu {x.group(1)}"
            return {**filter, **paramsObj}
    
    x = re.search("sim-luc-quy-(\d{6})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['title'] = f"{filter['title']} {filter['tail']}"
            return {**filter, **paramsObj}
    x = re.search("sim-luc-quy-(\d{6})-dau-(\d{2,3})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['h'] = x.group(2)
            filter['title'] = f"{filter['title']} {filter['tail']} đầu {x.group(2)}"
            return {**filter, **paramsObj}
    x = re.search("sim-luc-quy-dau-(\d{2,4})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['h'] = x.group(1)
            filter['title'] = f"{filter['title']} đầu {x.group(1)}"
            return {**filter, **paramsObj}
    # sim tu quy
    x = re.search("sim-tu-quy-(\d{4})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['title'] = f"{filter['title']} {filter['tail']}"
            return {**filter, **paramsObj}
    x = re.search("sim-tu-quy-(\d{4})-dau-(\d{2,})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['h'] = x.group(2)
            filter['title'] = f"{filter['title']} {x.group(1)} đầu {filter['h']}"
            return {**filter, **paramsObj}
    # sim tam hoa
    x = re.search("sim-tam-hoa-(\d{3})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['title'] = f"{filter['title']} {filter['tail']}"
            return {**filter, **paramsObj}
    x = re.search("sim-tam-hoa-(\d{3})-dau-(\d{2,3})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['h'] = x.group(2)
            filter['title'] = f"{filter['title']} {x.group(1)} đầu {filter['h']}"
            return {**filter, **paramsObj}
    x = re.search("sim-tam-hoa-dau-(\d{2,4})$", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['h'] = x.group(1)
            filter['title'] = f"{filter['title']} đầu {filter['h']}"
            return {**filter, **paramsObj}
    x = re.search("sim-nam-sinh-(\d{4})", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == url_path or item["link"] in url_path:
                filter = item.copy()
                break
        if filter:
            filter['tail'] = x.group(1)
            filter['title'] = f"{filter['title']} {filter['tail']}"
            return {**filter, **paramsObj}
    x = re.search("sim-([A-Za-z0-9-]{2,})+-(viettel|vinaphone|mobifone|itelecom|vietnamobile|gmobile)", url_path)
    if x:
        for item in SimsConfig.filterTypes:
            if item['link'] == f'/sim-{x.group(1)}':
                filter = item.copy()
                break
        if filter:
            for item1 in SimsConfig.filterTel:
                if item1['link'] == f'/sim-{x.group(2)}':
                    filter['t'] = item1['t']
                    filter['title'] = f"{filter['title']} {x.group(2).capitalize()}"
                    break
            return {**filter, **paramsObj}
    
    x = re.search("sim-(viettel|vinaphone|mobifone|itelecom|vietnamobile|gmobile)-dau-(\d{2,3})", url_path)
    if x:
        for item in SimsConfig.filterTel:
            if item['link'] == f'/sim-{x.group(1)}':
                filter = item.copy()
                break
        if filter:
            filter['h'] = x.group(2)
            filter['title'] = f"{filter['title']} đầu {x.group(2)}"
            return {**filter, **paramsObj}    
    x = re.search("sim-so-dep-dau-(\d{1,9})-giua-(\d{1,9})-duoi-(\d{1,9})$", url_path)
    if x:
        filter = {}
        filter['h'] = x.group(1)
        filter['mid'] = x.group(2)
        filter['tail'] = x.group(3)
        filter['link'] = url_path
        filter['title'] = f'Sim số đẹp đầu {x.group(1)} giữa {x.group(2)} đuôi {x.group(3)}'
        return {**filter, **paramsObj}    
    x = re.search("sim-so-dep-(\d{2,})-giua$", url_path)
    if x:
        filter = {}
        filter['mid'] = x.group(1)
        filter['link'] = url_path
        filter['title'] = f'Sim số đẹp {x.group(1)} giữa'
        return {**filter, **paramsObj}    
    x = re.search("sim-so-dep-duoi-(\d{1,})-dau-(\d{2,8})$", url_path)
    if x:
        filter = {}
        filter['tail'] = x.group(1)
        filter['h'] = x.group(2)
        filter['link'] = url_path
        filter['title'] = f'Sim số đẹp đuôi {x.group(1)} đầu {x.group(2)}'
        return {**filter, **paramsObj}    
    x = re.search("sim-so-dep-duoi-(\d{1,})-giua-(\d{2,8})$", url_path)
    if x:
        filter = {}
        filter['tail'] = x.group(1)
        filter['mid'] = x.group(2)
        filter['link'] = url_path
        filter['title'] = f'Sim số đẹp đuôi {x.group(1)} giữa {x.group(2)}'
        return {**filter, **paramsObj}    
    x = re.search("sim-so-dep-dau-(\d{2,})-duoi-(\d{2,7})$", url_path)
    if x:
        filter = {}
        filter['h'] = x.group(1)
        filter['tail'] = x.group(2)
        filter['link'] = url_path
        filter['title'] = f'Sim số đẹp đầu {x.group(1)} đuôi {x.group(2)}'
        return {**filter, **paramsObj}    
    x = re.search("sim-so-dep-dau-(\d{2,})-giua-(\d{2,7})$", url_path)
    if x:
        filter = {}
        filter['h'] = x.group(1)
        filter['mid'] = x.group(2)
        filter['link'] = url_path
        filter['title'] = f'Sim số đẹp đầu {x.group(1)} giữa {x.group(2)}'
        return {**filter, **paramsObj}    
    x = re.search("sim-so-dep-duoi-(\d{1,9})$", url_path)
    if x:
        filter = {}
        filter['tail'] = x.group(1)
        filter['link'] = url_path
        filter['title'] = f'Sim số đẹp đuôi {x.group(1)}'
        return {**filter, **paramsObj}   
     
    if filter is None:
        config_filters = SimsConfig.filterTypes + SimsConfig.filterTel + SimsConfig.filterPrice + SimsConfig.filterFates
        for item in config_filters:
            if item['link'] == url_path:
                filter = item.copy()
    # lay cau hinh filter config trong page
    if page and page.store_config:
        store_type = page.store_config.get('store_type', None)
        query_mandatory = page.store_config.get('query_mandatory', None)
        params_dict = {}
        if filter is None:
            filter = {}
        if query_mandatory:
            params_dict = parse_qs(query_mandatory)
            params_dict = {key: values[0] for key, values in params_dict.items()}
            params_dict = {key: str(value) for key, value in params_dict.items()}
        filter = {
            **filter,
            **params_dict,
            'store_type': store_type,
            'title': page.title,
        }
    if filter is None:
        filter = {}
    return {**filter, **paramsObj}


def convertArrayLogobyTheme(filterArray, theme_folder):
    arr = []
    for item in filterArray:
        itemCopy = item.copy()
        itemCopy["logo"] = item["logo"].replace("{theme_folder}", theme_folder)
        arr.append(itemCopy)
    return arr


def getSeo(page, tenant, context, head_title=None):
    default_title = head_title if head_title else tenant.site_name
    return {
        'title': parse_content(page.title if hasattr(page, 'title') else default_title, context),
        'h1': parse_content(page.title if hasattr(page, 'title') else default_title, context),
        'meta_title': parse_content(page.meta_title if hasattr(page, 'meta_title') else default_title, context),
        'meta_description': parse_content(page.meta_description if hasattr(page, 'meta_description') else tenant.theme_config.get('seo',{}).get('description',''), context),
        'meta_canonical': parse_content(page.meta_canonical if hasattr(page, 'meta_canonical') else None, context),
        'meta_keywords': parse_content(page.meta_keywords if hasattr(page, 'meta_keywords') else None, context),
        'headScript_page': parse_content(page.headscript if hasattr(page, 'headscript') else None, context),
        'headScript_tenant': parse_content(tenant.theme_config.get('seo',{}).get('headScript', ''), context),
        'footerScript_page': parse_content(page.footerScript if hasattr(page, 'footerScript') else None, context),
        'footerScript_tenant': parse_content(tenant.theme_config.get('seo',{}).get('footerScript',''), context)
    }
def parse_content(content, context):
    if content:
        template = Template(html.unescape(content))
        return template.render(Context(context))
    else:
        return content
def relatedPages(data):
    result = None
    if data:
        pairs = [line.split('|') for line in data.split('\n')]
        result = [{'title': pair[0], 'link': pair[1]} for pair in pairs if len(pair) > 1 and pair[1] and pair[1].strip() not in ['', '\r']]
    return result
def vn_date_format(value):
    if value is not None and len(str(value).strip()) > 0:
        return value.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return ''
def get_telco_text(t):
        return dict(NHA_MANG_CHOICES).get(t, '')
    
def get_list_cate(cats):
    list_cate = []
    for c in cats:
        list_cate.append(get_label_from_value(CATEGORY_CHOICES, c))
    return ", ".join(list_cate)

def keyword_to_url_params(keyword):
    arr = remove_duplicate_star(keyword).split('*')
    url = ""
    if len(arr) == 1 and len(keyword) > 0:
        url += f"&tail={keyword}"
    elif len(arr) == 2:
        url += f"&head={arr[0]}&tail={arr[1]}"
    elif len(arr) >= 3:
        url += f"&head={arr[0]}&middle={arr[1]}&tail={arr[2]}"
    return url
def keyword_to_object_params(keyword):
    arr = remove_duplicate_star(keyword).split('*')
    params_obj = {}
    if len(arr) == 1 and len(keyword) > 0:
        params_obj['tail'] = keyword
    elif len(arr) == 2:
        params_obj['h'] = arr[0]
        params_obj['tail'] = arr[1]
    elif len(arr) >= 3:
        params_obj['h'] = arr[0]
        params_obj['mid'] = arr[1]
        params_obj['tail'] = arr[2]
    return params_obj

def remove_duplicate_star(keyword):
    result = ''
    prev_char = ''
    for char in keyword:
        if char != '*' or char != prev_char:
            result += char
        prev_char = char
    return result

def get_date_filter(date):
    start_of_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start_of_date, end_of_date

def get_queryset_filter_date(parameter_name, value, queryset):
    now = (timezone.now() + timedelta(hours=7))
    if value == 'today':
        start_of_date,end_of_date = get_date_filter(now)
        return queryset.filter(**{parameter_name + '__gte': start_of_date, parameter_name + '__lte': end_of_date})
    elif value == 'yesterday':
        yesterday = now - timedelta(days=1)
        start_of_date,end_of_date = get_date_filter(yesterday)
        return queryset.filter(**{parameter_name + '__gte': start_of_date, parameter_name + '__lte': end_of_date})
    elif value == 'last_7_days':
        last_7_days = now - timedelta(days=7)
        return queryset.filter(**{parameter_name + '__gte': last_7_days})
    elif value == 'this_month':
        this_month = now.replace(day=1)
        return queryset.filter(**{parameter_name + '__gte': this_month})
    elif value == 'last_6_months':
        last_6_months = now - timedelta(days=180)
        return queryset.filter(**{parameter_name + '__gte': last_6_months})
    elif value == 'this_year':
        this_year = now.replace(month=1, day=1)
        return queryset.filter(**{parameter_name + '__gte': this_year})
    elif value == 'longer':
        longer = now.replace(month=1, day=1)
        return queryset.filter(**{parameter_name + '__lt': longer})