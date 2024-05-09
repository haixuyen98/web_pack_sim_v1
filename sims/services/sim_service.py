import os
import requests
from core.http_utils import session
from django.shortcuts import get_object_or_404
from urllib.parse import urlencode
from sims.models import SimOrder, SimStore
from django.db.models import Q
from django.core.paginator import Paginator
from blog.models import ArticlePage
from django.core.exceptions import ObjectDoesNotExist
from seo_optimizer.models import SeoProduct
from sims.common.choices import CATE_INSTALLMENT_ID, SIM_PRICE_DISPLAY_FIELD, DEFAULT_STORE_TYPE, STORE_TYPES, NHA_MANG_CHOICES, get_label_from_value
from sims.services.helpers import get_list_cate
import math

def getSims(paramsObj={}, tenant=None, request=None, api_path=None):
    data = {
        'data': [],
        'meta': {
            'total': 0,
            'page': 1,
            'limit': 0
        }
    }
    # start_time = time.time()  # Get the current time before calling the function
    store_type = paramsObj.get('store_type', None)
    sim_api_url = tenant.config['sim_api_url']
    sim_api_url = sim_api_url if sim_api_url is not None else os.environ.get('APPSIM_API_URL', '')
    if not api_path:
        sim_api_url = f"{sim_api_url}/search/query3/"
    else:
        sim_api_url = f"{sim_api_url}{api_path}/"
    if not store_type:
        store_config = tenant.config['store_config']
        store_type = store_config.get('store_type', DEFAULT_STORE_TYPE)
    store_type = int(store_type)
    default_limit = tenant.config.get("page_sim_limit", 50)
    if 'limit' not in paramsObj:
        paramsObj['limit'] = default_limit
    if store_type == STORE_TYPES.KHO_MIX:  # combine first simstore table, then to ES AppSim
        data = getMixSims(paramsObj, sim_api_url, tenant, request)
    elif store_type == STORE_TYPES.KHO_APPSIM:  # only ES APPSIM
        data = getAppSim(paramsObj, sim_api_url, tenant, request)

    elif store_type == STORE_TYPES.KHO_SIM:  # only in simstore table 
        data = getSimsStore(paramsObj, tenant, request)

    if 'from_admin' not in paramsObj or not paramsObj['from_admin']:
        priority_and_hide_sim_numbers(tenant, request, data)
    apply_verify_installment(data['data'], store_type)

    # end_time = time.time()  # Get the current time after the function call
    # total_time = end_time - start_time
    # print("Total time:", total_time, "seconds")
    return data

def apply_appsim_adjust_prices(tenant, sims_data, store_type):
    appsim_adjust_prices = tenant.config['appsim_adjust_prices']
    store_config = tenant.config['store_config'] if 'store_config' in tenant.config else None
    sim_price_display_field_name = store_config.get('sim_price_display_field', SIM_PRICE_DISPLAY_FIELD)
    allow_adjust_price_for_appsim = tenant.config.get("allow_adjust_price_for_appsim", 'off')

    for sim in sims_data:
        sim_price = sim[sim_price_display_field_name]
        sim['price'] = sim_price
        sim['price_calc'] = sim_price
        for adjust_price in appsim_adjust_prices:
            min_price = int(adjust_price.get('price_from')) if adjust_price.get('price_from', '') else 0
            max_price = int(adjust_price.get('price_to')) if adjust_price.get('price_to', '') else 0
            percent = int(adjust_price.get('percent')) if adjust_price.get('percent', '') else 0
            # neu la kho nha, thì ko app dung vs kho tra gop va chi app dung phan tram giam gia
            if min_price <= sim_price <= max_price and percent<0 and store_type==STORE_TYPES.KHO_SIM and CATE_INSTALLMENT_ID not in sim['c']:
                sim['price_calc'] = round(sim_price + sim_price * percent/100, -3)
                sim['adjust_percent'] = percent
                break
            if min_price <= sim_price <= max_price and store_type==STORE_TYPES.KHO_APPSIM:
                # ap dung % giam gia am (nen co the quet cả % duong)
                if allow_adjust_price_for_appsim !='off':
                    sim['price_calc'] = round(sim_price + sim_price * percent/100, -3)
                    sim['adjust_percent'] = percent
                # neu ko ap dung % giam gia am, thi chi check voi config gia % duong
                elif percent>0:
                    sim['price_calc'] = round(sim_price + sim_price * percent/100, -3)
                    sim['adjust_percent'] = percent
    return sims_data

def apply_verify_installment(sims_data, store_type):
    page = ArticlePage.pageManager.filter(slug="sim-tra-gop").first()
    if page:
        page_store_type = page.store_config.get('store_type',None)
        # neu page_store_type trong page sim-tra-gop = store_type truyen vao hoac = KHO_MIX
        # block sim tra gop homepage, thi tham so store_type se lay store_type trong page sim-tra-gop
        # con o trang detail thi truyen fix cung
        if int(page_store_type) == store_type or page_store_type==STORE_TYPES.KHO_MIX or store_type==STORE_TYPES.KHO_MIX:
            for sim_data in sims_data:
                if CATE_INSTALLMENT_ID in sim_data['c']:
                    sim_data['is_installment'] = True
                    sim_data['price_calc_installment'] = sim_data['price_calc']
    return sims_data

def priority_and_hide_sim_numbers(tenant=None, request=None, data=None):
    store_config = tenant.config['store_config'] if 'store_config' in tenant.config else None
    numbers_hidden = store_config.get("numbers_hidden", None) if store_config else None
    store_ignores = store_config.get("store_ignores", None) if store_config else None
    if 'data' in data:
        # hide sims in store cònig numbers_hidden
        if numbers_hidden:
            numbers_hidden = set(numbers_hidden.split('\r\n'))
            data['data'] = [item for item in data['data'] if item['id'] not in numbers_hidden]
        # apply detail page
        if store_ignores:
            store_ignores = store_ignores.split('\r\n')
            for item in data['data']:
                if 's3' in item and item['s3']:
                    if len(item['s3']) == 1:
                        value = item['s3'][0]
                        if str(value) in store_ignores :
                            data['data'].remove(item)
        # priority first display in priority_numbers
        store_config_page = getPageStoreConfigBySlug(request)
        if store_config_page:
            priority_numbers = store_config_page.get('priority_numbers', None)
            if priority_numbers and data['data']:
                data['data'] = sorted(data['data'], key=lambda x: priority_numbers.index(x['id']) if 'id' in x and x['id'] in priority_numbers else float('inf'))
    return data
def getPageStoreConfigBySlug(request=None):
    store_config_page=None
    if request:
        current_path = request.path.strip('/')
        try:
            page = ArticlePage.objects.get(slug=current_path)
            store_config_page = page.store_config
        except ObjectDoesNotExist:
            print("getPageBySlug page not exists")
    return store_config_page

def getPriorityQueryFromSimConfig(tenant=None, request=None, queryParams=None):
    store_config = tenant.config['store_config'] if 'store_config' in tenant.config else None
    store_config_page = getPageStoreConfigBySlug(request)
    if queryParams is None:
        queryParams = {
            'obj': {},
            'queryQ': {}
        }
    obj = queryParams["obj"]
    d = _getValueInDict('d', store_config, store_config_page)
    d = d if d else store_config['d']

    priority_numbers = store_config_page.get('priority_numbers', None) if store_config_page else None

    # priority_numbers = _getValueInDict('numbers_hidden', store_config, store_config_page)
    priority_stores = _getValueInDict('priority_stores', store_config, store_config_page)
    store_ignores = _getValueInDict('store_ignores', store_config, store_config_page)
    gte = _getValueInDict('gte', store_config, store_config_page)
    lte = _getValueInDict('lte', store_config, store_config_page)
    t = _getValueInDict('t', store_config, store_config_page)
    is_only_sale_stores = store_config.get('is_only_sale_stores', False) if store_config else None
    telco_rates = store_config.get('telco_rates', None) if store_config else None
    store = store_config.get('priority_stores', None) if store_config else None
    if 'direction' not in obj and d is not None:
        obj['direction'] = d
    if priority_numbers is not None:
        obj['priority_numbers'] = ','.join(priority_numbers.strip().split("\r\n"))
    if priority_stores is not None:
        obj['priority_stores'] = ','.join(priority_stores.strip().split("\r\n"))
    if is_only_sale_stores and len(store)>0:
        obj['store'] = ','.join(store.strip().split("\r\n"))
    if store_ignores:
        obj['notStore'] = ','.join(store_ignores.strip().split("\r\n"))
    telco_rate_value= {}
    if telco_rates:
        for key, value in telco_rates.items():
            telco_rate_value[key] = int(value) / 100 if value else 0
        obj['telco_rates'] = telco_rate_value
    custom_query = []
    if gte:
        custom_query.append(f"gte={gte}")
    if lte:
        custom_query.append(f"lte={lte}")
    if t:
        custom_query.append(f"t={t}")
    if len(custom_query)>0:
        obj['custom_query'] = '&'.join(custom_query)
    return queryParams

def _getValueInDict(property, store_config, store_config_page):
    if store_config_page is not None:
        result = store_config_page.get(property,None)
        if result and isinstance(result, str):
            result = result.strip()
    elif store_config is not None:
        result = store_config.get(property, None)
        if result:
            result = result.strip()
    else:
        result = None
    return result

def getMixSims(paramsObj={},sim_api_url=None, tenant=None, request=None):
    data = getSimsStore(paramsObj, tenant, request)
    # neu so sim trong db postges < 10 thi get them tren appsim els
    if len(data['data'])<10:
        total = data['meta']['total']
        limit = data['meta']['limit']
        sim_store_total_page = math.ceil(int(total) / int(limit))
        current_page = int(paramsObj.get('p', 1))
        paramsObj['p'] = current_page - sim_store_total_page
        data1=getAppSim(paramsObj, sim_api_url, tenant, request)

        if 'data' in data1:
            data['data'] = list(data['data']) + data1['data']
            data['meta']['total'] = data['meta']['total'] + data1['meta']['total']
    # mac dinh tong so sim tim duoc tren kho la 1000.000, tranh truong hop phai query lai appsim lay tong so sim
    if 'from_admin' not in paramsObj or not paramsObj['from_admin']:
        data['meta']['total'] = 1000000
    data['meta']['limit'] = paramsObj['limit']
    return data

def getSimsStore(paramsObj={}, tenant=None, request=None):
    limit = paramsObj['limit']
    page_number = int(paramsObj['p']) if 'p' in paramsObj else 1
    store_config = tenant.config['store_config'] if 'store_config' in tenant.config else None
    sim_price_display_field_name = store_config.get('sim_price_display_field', SIM_PRICE_DISPLAY_FIELD)

    queryParams = _getQueryParam(paramsObj, tenant)
    queryParams = getPriorityQueryFromSimConfig(tenant, request, queryParams)

    queryset = SimStore.objects.filter(queryParams['queryQ'])  
    queryset = queryset.filter(h=False, d=False)
    if queryParams['obj'].get('direction', None) is not None and queryParams['obj'].get('direction', None)!='0':
        sort_field = "pb"
        sort_order = "-" if queryParams['obj'].get('direction', None)=='1' else ''
        queryset = queryset.order_by(f'{sort_order}{sort_field}')
    paginator = Paginator(object_list=queryset, per_page=limit, allow_empty_first_page=True)
    total_page = paginator.num_pages
    page = []
    # neu total page >0 va p nho hon page thi moi lay ra, ko sẽ bị emptypage exception
    transformed_list = []
    if total_page>0 and page_number<= total_page:
        page = paginator.page(page_number)
        # Convert and transform each object in the page
        for obj in page.object_list:
            transformed_item = {
                'id': obj.id,
                'f': obj.f,
                'pb': obj.pb,
                'pn': obj.pn,
                't': obj.t,
                'd': obj.d,
                'c2': obj.c2,
                'c': obj.c,
                'h': obj.h,
                'tt': obj.tt,
                'k': obj.k,
                'h': obj.h,
                'price_calc': getattr(obj,sim_price_display_field_name, 0),
                'publish': obj.publish,
                'telcoText': get_label_from_value(NHA_MANG_CHOICES, obj.t),
                'cText': get_list_cate(obj.c),
            }
            transformed_list.append(transformed_item)
    
    allow_adjust_price_for_khosim = tenant.config.get("allow_adjust_price_for_khosim", 'off')
    print('allow_adjust_price_for_khosim', allow_adjust_price_for_khosim)
    if allow_adjust_price_for_khosim !='off':
        apply_appsim_adjust_prices(tenant, transformed_list, STORE_TYPES.KHO_SIM)
    data = {
        'data': transformed_list,
        'meta': {
            'total': queryset.count(),
            'page': page_number,
            'limit': limit
        }
    }
    return data

def getAppSim(paramsObj={}, sim_api_url=None, tenant=None, request=None):
    responseJson = {
        'data': [],
        'meta': {
            'total': 0,
            'page': 1,
            'limit': 0
        }
    }
    store_config = tenant.config['store_config'] if 'store_config' in tenant.config else None
    if store_config:
        acceptKhoAn = store_config.get('acceptKhoAn', False)
        paramsObj['acceptKhoAn'] = acceptKhoAn
    queryParams = _getQueryParam(paramsObj, tenant)
    queryParams = getPriorityQueryFromSimConfig(tenant, request, queryParams)
    query_object = queryParams['obj']
    # tim kiem tu admin
    if 'from_admin' in paramsObj and paramsObj['from_admin']:
        if 'notStore' in query_object:
            del query_object['notStore']
        if 'priority_stores' in query_object:
            del query_object['priority_stores']
        if 'telco_rates' in query_object:
            del query_object['telco_rates']
        if 'direction' in query_object:
            del query_object['direction']
    try:
        api_api_url = f'{sim_api_url}?{urlencode(query_object)}'
        header = {}
        result = session.get(api_api_url, timeout=15, headers=header)
        if result.status_code == 200:
            jsondata = result.json()
            if 'success' in jsondata and jsondata['success'] == True:
                responseJson = jsondata
                # apply adjust price
                responseJson['data']= apply_appsim_adjust_prices(tenant, responseJson['data'], STORE_TYPES.KHO_APPSIM)
    except requests.exceptions.Timeout as e:
        print ("Http Error:", e)
    except requests.exceptions.TooManyRedirects as e:
        print ("Http Error:", e)
    except requests.exceptions.RequestException as e:
        print ("Http Error:", e)
    return responseJson

def getSellerInfo(agency_ids, sim_api_url=None):
    if bool(agency_ids) is False:
        return None
    try:
        api_api_url = sim_api_url if sim_api_url is not None else os.environ.get('APPSIM_AGENCY_API_URL', 'https://api.appsim.net')
        api_api_url = f'{api_api_url}/v1/api/web/search/info-agency'
        header = {}
        payload = {
            'agency_ids': agency_ids
        }
        result = session.get(api_api_url, timeout=15, headers=header, json=payload)
        if result.status_code == 200:
            jsondata = result.json()
            if 'success' in jsondata and jsondata['success'] == True:
                responseJson = jsondata
                # apply adjust price
                return responseJson['data']
    except requests.exceptions.Timeout as e:
        print ("Http Error:", e)

def getPhoneInfo(phones, tenant, sim_api_url=None):
    if bool(phones) is False:
        return {}
    
    if 'sim_api_url' in tenant.config:
        sim_api_url = tenant.config['sim_api_url']

    try:
        api_api_url = sim_api_url if sim_api_url is not None else os.environ.get('APPSIM_API_URL', '')
        api_api_url = f'{api_api_url}/search/query3-not-mix/?in_numbers={phones}'
        header = {}
        result = session.get(api_api_url, timeout=15, headers=header)
        if result.status_code == 200:
            jsondata = result.json()
            responseJson = jsondata
            # apply adjust price
            grouped_data = {}
            if 'success' in jsondata and jsondata['success'] == True:
                data_list = responseJson['data']
                for item in data_list:
                    id_value = item['id']
                    s_value = item['s'] if 's' in item else []

                    for value in s_value:
                        pg = value.get('pg')
                        pb = value.get('pb')

                        if pg is not None and pb is not None:
                            value["pi"] = pb - pg

                    if id_value in grouped_data:
                        grouped_data[id_value].extend(s_value)
                    else:
                        grouped_data[id_value] = s_value
                return grouped_data
    except requests.exceptions.Timeout as e:
        print ("Http Error:", e)

def _getQueryParam(paramsObj={}, tenant=None):
    obj = {}
    query = Q()
    store_config = tenant.config['store_config'] if 'store_config' in tenant.config else None
    sim_price_display_field_name = store_config.get('sim_price_display_field', SIM_PRICE_DISPLAY_FIELD)
    l_sec = int(store_config.get('l_sec_gte','0'))
    # query theo thoi gian cap nhat (ap dung cho kho appsim thoi)
    if l_sec > 0:
        obj['l_sec'] = l_sec

    if paramsObj.get('c', None) is not None:
        obj['catId'] = paramsObj['c']
        q_list = [Q(c__contains=[item]) for item in obj['catId'].split(',')]
        array_query = Q()
        for q in q_list:
            array_query |= q
        query = query & array_query

    if paramsObj.get('acceptKhoAn', None) is not None:
        obj['acceptKhoAn'] = paramsObj['acceptKhoAn']

    if paramsObj.get('h', None) is not None:
        obj['head'] = paramsObj['h']
        q_list = [Q(id__startswith=item) for item in obj['head'].split(',')]
        array_query = Q()
        for q in q_list:
            array_query |= q
        query = query & array_query
    if paramsObj.get('tail', None) is not None:
        obj['tail'] = paramsObj['tail']
        q = Q(id__endswith=obj['tail'])
        query = query & q
    if paramsObj.get('mid', None) is not None:
        obj['middle'] = paramsObj['mid']
        query = Q(id__contains=f'{obj["middle"]}')

    if paramsObj.get('s', None) is not None:
        obj['store'] = paramsObj['s'].strip()
    if paramsObj.get('t', None) is not None:
        obj['t'] = paramsObj['t'].strip()
        q_list = [Q(t=item) for item in obj['t'].split(',')]
        array_query = Q()
        for q in q_list:
            array_query |= q
        query = query & array_query
        
    if paramsObj.get('query', None) is not None:
        obj['query'] = ','.join(paramsObj['query'])
    if paramsObj.get('queryNotIn', None) is not None:
        obj['queryNotIn'] = ','.join(paramsObj['queryNotIn'])
    # if paramsObj.get('link', None) is not None:
    #     obj['link'] = paramsObj['link']
    if paramsObj.get('p', None) is not None:
        obj['page'] = paramsObj['p']
    if paramsObj.get('d', None) is not None:
        obj['direction'] = paramsObj['d']
        obj['sortBy'] = sim_price_display_field_name
    if paramsObj.get('notInCates', None) is not None:
        obj['notInCates'] = paramsObj['notInCates']
    if paramsObj.get('limit', None) is not None:
        obj['limit'] = paramsObj['limit']
    if paramsObj.get('pr', None) is not None:
        obj['prices'] = paramsObj['pr']
        q_list = [Q(pb__range=(int(item.split("-")[0]), int(item.split("-")[1]))) for item in obj['prices'].split(',')]
        array_query = Q()
        for q in q_list:
            array_query |= q
        query = query & array_query
        
    if paramsObj.get('cf', None) is not None:
        obj['catFate'] = paramsObj['cf']
        q_list = [Q(c__contains=[item]) for item in obj['catFate'].split(',')]
        array_query = Q()
        for q in q_list:
            array_query |= q
        query = query & array_query
    if paramsObj.get('yc', None) is not None:
        obj['yearCom'] = paramsObj['yc']
    obj['gte'] = 1
    obj['price_key'] = sim_price_display_field_name
    return {
        'obj': obj,
        'queryQ': query
    }

def getSimDetail(simId, tenant=None):
    response_json = None
    sim_api_url = tenant.config['sim_api_url']
    store_config = tenant.config['store_config'] if 'store_config' in tenant.config else None
    sim_price_display_field_name = store_config.get('sim_price_display_field', SIM_PRICE_DISPLAY_FIELD)
    try:
        sim_instance = SimStore.objects.get(id=simId,d=False, h=False)
        response_json = sim_instance.__dict__
        response_json['telcoText'] = sim_instance.telcoText
        response_json['categoryText'] = sim_instance.categoryText
        response_json['price_calc'] = getattr(sim_instance, sim_price_display_field_name, 0)
        response_json['price'] = response_json['price_calc']
        response_json['store_type'] = STORE_TYPES.KHO_SIM
        allow_adjust_price_for_khosim = tenant.config.get("allow_adjust_price_for_khosim", 'off')
        if allow_adjust_price_for_khosim:
            apply_appsim_adjust_prices(tenant, [response_json], STORE_TYPES.KHO_SIM)
        if CATE_INSTALLMENT_ID in response_json['c']:
            apply_verify_installment([response_json], STORE_TYPES.KHO_SIM)
        
    except SimStore.DoesNotExist:
        try:
            # get sim from appsim
            if simId:
                store_config = tenant.config['store_config'] if 'store_config' in tenant.config else None
                acceptKhoAn = False
                if store_config:
                    acceptKhoAn = store_config.get('acceptKhoAn', False)                    
                l_sec = int(store_config.get('l_sec_gte','0'))
                api_api_url = sim_api_url if sim_api_url is not None else os.environ.get('APPSIM_API_URL', '')
                api_api_url = f'{api_api_url}/detail/index-no-seo?sim={simId}&l_sec={l_sec}'
                if acceptKhoAn:
                    api_api_url = f'{api_api_url}&acceptKhoAn={acceptKhoAn}'
                header = {}
                result = session.get(api_api_url, headers=header)
                if result.status_code == 200:
                    simInfo = result.json()['data']['simInfo']
                    response_json = simInfo.get('detail',None)
                    if response_json:
                        data_apply = apply_appsim_adjust_prices(tenant, [response_json], STORE_TYPES.KHO_APPSIM)
                        response_json = data_apply[0]
                        response_json['store_type'] = STORE_TYPES.KHO_APPSIM
                        if CATE_INSTALLMENT_ID in response_json['c']:
                            apply_verify_installment([response_json], STORE_TYPES.KHO_APPSIM)
        except requests.exceptions.Timeout as e:
            print("Http Error:", e)
        except requests.exceptions.TooManyRedirects as e:
            print("Http Error:", e)
        except requests.exceptions.RequestException as e:
            print("Http Error:", e)
    
    if response_json:
        seo_config = _getDetailSeo(response_json)
        response_json['seo_config'] = seo_config
        data = {
            'data': [response_json]
        }
        data = priority_and_hide_sim_numbers(tenant, None, data)
        if len(data['data'])>0:
            return data['data'][0]
    return None

def _getDetailSeo(sim):
    # description =f'{sim["id"]} thuộc nhà mạng {sim["telcoText"]} với đầu số {sim["id"][:4]} và loại {sim["categoryText"]} với đuôi số {sim["id"][-4:]}'
    # if sim['pb']!=0:
    #     description += f" có giá bán tại sSIMvn là {sim['priceFormatted']}"
    # description += ". Đăng ký chính chủ và Giao sim Miễn Phí toàn quốc"
    # title = f"Sim {sim['id']} - {sim['categoryText']} {sim['f']}"
    # h1 = title
    # data = {
    #     'title': title,
    #     'description': description,
    #     'h1': h1,
    #     'thumbnail': f"https://static.simthanglong.vn/{sim['id']}.jpg",
    # }
    seo_config = None
    data = None
    try:
        seo_config = SeoProduct.objects.filter(
            Q(min_price__lte=sim['price']) & Q(max_price__gte=sim['price']) & Q(c2__exact=int(sim['c2']))
        ).first()
        data = {}
    except ObjectDoesNotExist:
        seo_config = None
    
    if seo_config:
        data['title'] = seo_config.title
        data['meta_description'] = seo_config.description
        data['h1'] = seo_config.h1
    return data

def getSimValuation(sim, tenant, sim_api_url=None):
    responseJson = {}
    if 'sim_api_url' in tenant.config:
        sim_api_url = tenant.config['sim_api_url']
    try:
        api_api_url = sim_api_url if sim_api_url is not None else os.environ.get('APPSIM_API_URL', '')
        api_api_url = f'{api_api_url}/valuation/index?sim={sim}'
        header = {}
        result = session.get(api_api_url, headers=header)
        if result.status_code == 200:
            responseJson = result.json()['data']
    except requests.exceptions.Timeout as e:
        print ("Http Error:", e)
    except requests.exceptions.TooManyRedirects as e:
        print ("Http Error:", e)
    except requests.exceptions.RequestException as e:
        print ("Http Error:", e)
    return responseJson


def getOrderDetail(code):
    return get_object_or_404(SimOrder, code=code)
