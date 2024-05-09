from sims.services.sim_service import getSims, getSimDetail, getOrderDetail, getSimValuation
from blog.models import ArticlePage
from sims.services.helpers import getSimUrlFilter, getSeo, relatedPages, parse_content
import html
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import SimOrder
from django.http import Http404
from django.core.exceptions import ValidationError
from sims.common.choices import (
    STATUS_CHOICES,
    REQUEST_CHOICES,
    STORE_TYPES,
    INSTALLMENT_TYPE_CHOICES
)
from django_tenants.utils import remove_www
from django.views.decorators.cache import cache_page, never_cache
from core.helpers import get_client_ip
from sims.forms import FengShuiForm, FengShuiFortuneForm
import requests
import json
import os
from datetime import datetime
from .utils import check_order_exist_ago, check_trans_mb_exist_ago
from core.helpers import decrypt_data, encrypt_data

# Create your views here.
@cache_page(60 * 15)
def homePage(request):
    tenant = request.tenant
    paramsObj = request.GET.dict()
    change_url = reverse('admin:blog_article_change', args=({'slug':'homepage'}))
    context = {
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'request': request,
        'change_url': change_url,
        'tenant': tenant
    }
    # if no params in url
    if not paramsObj or 'loginToken' in paramsObj:
        # neu co page template thi parse template from db
        page = ArticlePage.pageManager.filter(slug=f'homepage',).first()
        if page:
            context['page'] = page
            context['content'] = parse_content("{% load sims_tags %}" + html.unescape(page.body), context)
        context['seo'] = getSeo(page, tenant, context)
        return render(request, f'{tenant.theme_folder}/index.html', context)
    else:  # search sim
        filterObj = getSimUrlFilter(request.path, paramsObj)
        response_data = getSims(filterObj, tenant, request)
        context = {
            'listSim': response_data['data'],
            'theme_folder': tenant.theme_folder,
            'theme_config': tenant.theme_config,
            'request': request,
            'meta_data': response_data['meta'],
            'page': {},
            'seo': {},
            'tenant': tenant
        }
        context['seo'] = getSeo(filterObj, tenant, context)
        return render(request, f'{tenant.theme_folder}/sim-slug.html', context)


# Create your views here.
@cache_page(60 * 15)
def simListPage(request, slug):
    tenant = request.tenant
    page = ArticlePage.pageManager.filter(slug=f'sim-{slug}').first()
    paramsObj = request.GET.dict()
    filterObj = getSimUrlFilter(request.path, paramsObj, page)
    # neu ko tim thay config filter or page
    if 'title' not in filterObj:
        raise Http404("Page not found")

    response_data = getSims(filterObj, tenant, request)
    listSim = response_data['data']
    meta_data = response_data['meta']
    head_title = filterObj['title'] if filterObj and 'title' in filterObj else ''
    context = {
        'listSim': listSim,
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'request': request,
        'pages': {},
        'meta_data': meta_data,
        'head_title': head_title,
        'tenant': tenant
    }
    
    breadcrumb_data = [
        {'title': 'Trang chủ', 'href': '/'},
        {'title': head_title, 'href': ''},
    ]
    if page:
        context['page'] = page
        context['excerpt'] = parse_content(html.unescape(page.excerpt), context)
        context['relatedPages'] = relatedPages(page.related_pages)
        context['content'] = parse_content(html.unescape(page.body), context)
    context['breadcrumb_data'] = breadcrumb_data

    context['seo'] = getSeo(page, tenant, context, head_title)
        
    return render(request, f'{tenant.theme_folder}/sim-slug.html', context)

@never_cache
def simDetailPage(request, simNumber):
    tenant = request.tenant
    try:
        data = getSimDetail(simNumber, tenant)
        if not data:
            page = ArticlePage.pageManager.filter(slug="sim-does-not-exist").first()
            disable_sidebar_article = True
            context = {
                'tenant': tenant,
                'sim': simNumber,
                'theme_folder': tenant.theme_folder,
                'theme_config': tenant.theme_config,
                'request': request,
                'disable_sidebar_article': disable_sidebar_article
            }
            context['seo'] = getSeo(page, tenant, context)
            context['content'] = parse_content(html.unescape(page.body), context)
            return render(request, f'{tenant.theme_folder}/blog/page.html', context)
        # get url submit form
        submit_url = reverse("sims:submitSimOrder", kwargs={'sim': data['id']})
        secret_key = normalize_key_length(os.environ.get('SECRET_KEY', "data12kldsfjlsd!@31"))
        
        # get thong tin mb để tự động fill dữ liệu vào form
        mb_user_name = decrypt_data(request.COOKIES.get('mb_user_name',''), secret_key)
        mb_user_phone = decrypt_data(request.COOKIES.get('mb_user_phone',''), secret_key)
        # neu co thong tin info cua mb (Check phone) thi submit_url trong form se sang banking_afilate     
        if mb_user_phone:
            submit_url = reverse("banking_affiliate:submitSimOrder", kwargs={'sim': data['id']})
        # kiem tra neu ban qua mb thi check don da ton tại trong order or transaction 5 ngay ko
        config = request.tenant.config
        allow_sale_via_bank = config.get("allow_sale_via_bank", 'off')
        if allow_sale_via_bank=="on" or allow_sale_via_bank==True:
            # vs ban tren mb, sẽ check đơn tồn tại trong 5 ngày thì số đó đã được mua
            order_exist = check_order_exist_ago(sim=simNumber)            
            trans_exist = check_trans_mb_exist_ago(sim=simNumber)
            if order_exist or trans_exist:
                return redirect(f'{reverse("sims:viewPage", args=["sim-does-not-exist"])}',status=404)
        context = {
            'sim': data,
            'tenant': tenant,
            'theme_folder': tenant.theme_folder,
            'theme_config': tenant.theme_config,
            'config': tenant.config,
            'request': request,
            'page': {},
            'submit_url': submit_url,
            'head': data["f"][:3],
            'tail': data["f"][3:],
            'customer': {
                'name': mb_user_name,
                'phone': mb_user_phone
            }
        }
        page = ArticlePage.pageManager.filter(slug=f'trang-sim-detail').first()
        breadcrumb_data = [
            {'title': 'Trang chủ', 'href': '/'},
            {'title': f'Sim số đẹp {simNumber}', 'href': ''},
        ]
        if page:
            context['page'] = page
            context['content'] = parse_content(html.unescape(page.body), context)
            context['seo'] = getSeo(page, tenant, context)
            # neu config seo trong muc seo san pham
            if data['seo_config']:
                context['seo']['title'] = parse_content(data['seo_config']['title'], context)
                context['seo']['h1'] = parse_content(data['seo_config']['h1'], context)
                context['seo']['meta_description'] = parse_content(data['seo_config']['meta_description'], context)
                context['seo']['thumbnail'] = data['seo_config'].get('thumbnail', '')
            context['breadcrumb_data'] = breadcrumb_data
        return render(request, f'{tenant.theme_folder}/sim-detail.html', context)
    except KeyError:
        return redirect(f'{reverse("sims:viewPage", args=["sim-does-not-exist"])}',status=404)

@cache_page(60 * 15)
def viewPage(request, slug):
    tenant = request.tenant
    context = {
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'request': request,
    }
    page = ArticlePage.pageManager.filter(slug=slug).first()
    breadcrumb_data = [
        {'title': 'Trang chủ', 'href': '/'},
    ]
    if page.category:
        breadcrumb_data.append({'title': page.category, 'href': f'/tin-tuc/c/{page.category.slug}'})
    else:
        breadcrumb_data.append({'title': 'Tin tức', 'href': '/tin-tuc/'})
    breadcrumb_data.append({'title': page.title, 'href': ''})

    if slug != 'not-found':
        context['show_title'] = True
        context['breadcrumb_data'] = breadcrumb_data

    if page:
        context['page'] = page
        context['tenant'] = tenant
        context['content'] = parse_content(html.unescape(page.body), context)
    context['seo'] = getSeo(page, tenant, context)
    return render(request, f'{tenant.theme_folder}/blog/page.html', context)


def passSimOrderPage(request):
    tenant = request.tenant
    # logging.info("request============>", request.GET, request.COOKIES)
    secret_key = normalize_key_length(os.environ.get('SECRET_KEY', "data12kldsfjlsd!@31"))
    sim_number = decrypt_data(request.COOKIES.get('value_sim',''), secret_key)
    data = getSimDetail(sim_number, tenant)
    code = decrypt_data(request.COOKIES.get('sim_order_code',''), secret_key)
    orderData = None
    disable_sidebar_article = True
    try:
        orderData = getOrderDetail(code)
    except (ValueError, Http404) as e:
        print(f"Order {code} not found!")

    context = {
        'tenant': tenant,
        'sim': data,
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'request': request,
        'disable_sidebar_article': disable_sidebar_article,
        'order': orderData
    }
    if not orderData:
        page = ArticlePage.pageManager.filter(slug="sim-does-not-exist").first()
        context['seo'] = getSeo(page, tenant, context)
        context['content'] = parse_content(html.unescape(page.body), context)
        return render(request, f'{tenant.theme_folder}/blog/page.html', context)
    elif orderData.order_type==REQUEST_CHOICES.INSTALLMENT:
        page = ArticlePage.pageManager.filter(slug="dat-sim-thanh-cong-tra-gop").first()
        context['page'] = page
        context['content'] = parse_content(html.unescape(page.body), context)
        context['seo'] = getSeo(page, tenant, context)
    else:
        page = ArticlePage.pageManager.filter(slug="dat-sim-thanh-cong").first()
        context['page'] = page
        context['content'] = parse_content(html.unescape(page.body), context)
        context['seo'] = getSeo(page, tenant, context)
    return render(request, f'{tenant.theme_folder}/blog/page.html', context)


def failSimOrderPage(request):
    tenant = request.tenant
    sim_number = request.GET.get('sim')
    message = None
    disable_sidebar_article = True
    # classify each fail order
    error_code = request.GET.get('error')
    if error_code:
        if error_code == 'existed':
            message = "Xin lỗi, bạn đã đặt sản phẩm này trước đó. Vui lòng tìm kiếm các sản phẩm khác của chúng tôi."
        elif error_code == 'bad-request':
            message = "Đơn hàng không thể được xử lý do sản phẩm hiện đã bán hết. Vui lòng tìm kiếm các sản phẩm khác của chúng tôi."
        elif error_code == 'order_duplicate':
            message = "Đơn hàng không thể được xử lý do sản phẩm hiện đã bán hết. Vui lòng tìm kiếm các sản phẩm khác của chúng tôi."
        elif error_code == 'err400':
            message = "Số điện thoại đặt hàng trùng trùng với số sim của đơn hàng này. Vui lòng nhập số điện thoại hợp lệ."
    # define context
    context = {
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'request': request,
        'message': message,
        'sim_number': sim_number,
        'disable_sidebar_article': disable_sidebar_article,
    }
    page = ArticlePage.pageManager.filter(slug="dat-sim-that-bai").first()

    if page:
        context['page'] = page
        context['tenant'] = tenant
        context['content'] = parse_content(html.unescape(page.body), context)
        context['seo'] = getSeo(page, tenant, context)
    return render(request, f'{tenant.theme_folder}/blog/page.html', context)

def normalize_key_length(secret_key):
    # Nếu độ dài của secret_key nhỏ hơn 32 bytes, thêm ký tự '0' cho đến khi đủ
    while len(secret_key) < 32:
        secret_key += '0'
    # Trả về 32 bytes đầu tiên của secret_key
    return secret_key[:32]

# khi nhấn submit đặt sim sẽ chạy vào đây
def submitSimOrder(request, sim):
    tenant = request.tenant
    required_fields = ['name', 'phone']
    if request.POST.get('phone') == sim:
        return redirect(f'{reverse("sims:failSimOrderPage")}?sim={sim}&error=err400')
    existing_order = SimOrder.objects.filter(
        sim=sim,
        phone=request.POST.get('phone'),
        status__in=[STATUS_CHOICES.NEW, STATUS_CHOICES.PROCESSING]
    ).first()
    if existing_order:
        return redirect(f'{reverse("sims:failSimOrderPage")}?sim={sim}&error=existed')
    
    if request.method == 'POST' and all(request.POST.get(field) for field in required_fields):
        try:
                # Use the default value for the code field
                data = getSimDetail(sim, tenant)
                is_order_installment = request.POST.get('_is_installment')
                installment_info={}
                order_type = REQUEST_CHOICES.COMMON
                if is_order_installment is not None and is_order_installment.strip()!="":
                    installment_info={
                        "percentUpfront": request.POST.get('percentage'),
                        "monthNumber": request.POST.get('numberMonth'),
                        "installment_type": data.get('installment_type', INSTALLMENT_TYPE_CHOICES.PERCENT),
                        "iir": data.get('iir', 2), # mac dinh neu ko config se la 2%
                        "lpi": data.get('lpi', 2), # mac dinh neu ko config se la 2%
                    }
                    order_type = REQUEST_CHOICES.INSTALLMENT             
                if data:
                    if data['store_type'] == STORE_TYPES.KHO_APPSIM:
                        installment_info['pg'] = data.get('pg', '')

                        s_list = data.get('s', [])
                        if isinstance(s_list, list) and s_list:
                            max_pg_item = max(s_list, key=lambda x: x.get("pb", 0) - x.get("pg", 0))
                            max_pg_id = max_pg_item.get("id", None)
                            if max_pg_id is not None:
                                installment_info['agency_id'] = [max_pg_id]

                    sim_order = SimOrder.objects.create(
                        sim=sim,
                        phone=request.POST.get('phone'),
                        amount=data['price_calc'],
                        order_type=order_type,
                        name=request.POST.get('name'),
                        address=request.POST.get('address'),
                        other_option=request.POST.get('other_option', ''),
                        ip=get_client_ip(request),
                        pushed=0,
                        store_type=data['store_type'],
                        source_text=remove_www(request.get_host().split(':')[0]),
                        telco_id=data['t'],
                        c2=data['c2'],
                        attributes=installment_info
                    )
                response = redirect(f'{reverse("sims:passSimOrderPage")}')
                secret_key = normalize_key_length(os.environ.get('SECRET_KEY', "data12kldsfjlsd!@31"))
                response.set_cookie('sim_order_code', encrypt_data(sim_order.code, secret_key), max_age=600) #thoi gian het han cookies la 10p
                response.set_cookie('value_sim', encrypt_data(sim, secret_key), max_age=600)
                return response
                # return redirect(f'{reverse("sims:passSimOrderPage")}?sim={sim}&code={sim_order.code}')
        except ValidationError as e:
            pass
    # Redirect to failure page for any validation error or if required fields are not provided
    return redirect(f'{reverse("sims:failSimOrderPage")}?sim={sim}&error=bad-request')

@cache_page(60 * 15)
def fengShuiPage(request):
    tenant = request.tenant
    page = ArticlePage.pageManager.filter(slug=f'sim-phong-thuy').first()
    breadcrumb_data = [
        {'title': 'Trang chủ', 'href': '/'},
        {'title': 'Sim phong thuỷ', 'href': ''},
    ]
    response_data = None
    if request.method == 'POST':
        form = FengShuiForm(request.POST)
        if form.is_valid():
            birthday = form.cleaned_data['birthday']
            birth_time = form.cleaned_data['appt']
            sex = form.cleaned_data['sex']
            sex_mapping = {
                'men': 1,
                'women': 0,
            }
            sex = sex_mapping.get(sex.lower(), 1)
            birthday_str = birthday.strftime('%d-%m-%Y')
            sim_data = {
                "ngay_sinh": birthday_str,
                "gio_sinh": birth_time.strftime('%H:%M'),
                "gioi_tinh": sex,
                "phut_sinh": "00",
                "ho_ten": "Sim Thang Long",
                "sid": "4201,4281"
            }
            api_url = os.environ.get('PHONG_THUY_API_URL', "")
            api_url = f'{api_url}/search/sim'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, headers=headers, data=json.dumps(sim_data))
            response_data = response.json()
            request.session['form_data'] = request.POST
            request.session['response_data'] = response_data
    else:
        form = FengShuiForm(initial=request.session.get('form_data'))
    response_data = request.session.get('response_data')
    form_data = request.session.get('form_data', {})
    if form_data:
        del request.session['form_data']
    if response_data:
        del request.session['response_data']
    context = {
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'tenant': tenant,
        'breadcrumb_data': breadcrumb_data,
        'form': form,
        'form_data': form_data,
    }

    if page:
        context['page'] = page
        context['tenant'] = tenant
        context['content'] = parse_content(html.unescape(page.body), context)
        context['relatedPages'] = relatedPages(page.related_pages)
    context['seo'] = getSeo(page, tenant, context)
    context['dataSim'] = response_data.get('data', {}) if response_data else {}
    return render(request, f"{tenant.theme_folder}/fengShui.html", context)

@cache_page(60 * 15)
def SimFortunePage(request):
    tenant = request.tenant
    page = ArticlePage.pageManager.filter(slug=f'xem-phong-thuy').first()
    fortune_data = None
    if request.method == 'GET':
        sim = request.GET.get('sim')
        birthday = request.GET.get('birth_date')
        birth_time = request.GET.get('birth_time')
        birth_time_str = datetime.strptime(birth_time, '%H:%M')
        gio_sinh = birth_time_str.hour
        phut_sinh = birth_time_str.minute
        sex = request.GET.get('sex')
        sex_mapping = {
            'men': 1,
            'women': 0,
        }
        sex = sex_mapping.get(sex.lower(), 1)
        sim_data = {
            "ngay_sinh": birthday,
            "gio_sinh": gio_sinh,
            "gioi_tinh": sex,
            "phut_sinh": phut_sinh,
            "ho_ten": "Sim Thang Long",
            "so_sim": sim,
        }
        api_url = os.environ.get('PHONG_THUY_API_URL', "")
        api_url = f'{api_url}/tool/boisim'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(api_url, headers=headers, data=json.dumps(sim_data))
        fortune_data = response.json()
        request.session['fortune_data'] = fortune_data
    else:
        return redirect(f'/')
    
    if fortune_data:
        del request.session['fortune_data']
    
    context = {
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'sim': request.GET.get('sim')
    }
    if page:
        context['page'] = page
        context['tenant'] = tenant
        context['content'] = parse_content(html.unescape(page.body), context)
        context['relatedPages'] = relatedPages(page.related_pages)
    context['seo'] = getSeo(page, tenant, context)
    context['fortuneData'] = fortune_data.get('data', {}) if fortune_data else {}
    return render(request, f'{tenant.theme_folder}/SimFortune.html', context)

@cache_page(60 * 15)
def SimFengShuiFortunePage(request):
    tenant = request.tenant
    page = ArticlePage.pageManager.filter(slug='boi-phong-thuy-sim').first()

    if request.method == 'POST':
        form = FengShuiFortuneForm(request.POST)
        if form.is_valid():
            sim = form.cleaned_data['phone']
            birthday = form.cleaned_data['birthday']
            birthday_str = birthday.strftime('%d-%m-%Y')
            birth_time = form.cleaned_data['appt']
            birth_time_str = birth_time.strftime('%H:%M')
            sex = form.cleaned_data['sex']
            return redirect(f'/xem-phong-thuy/?sim={sim}&birth_date={birthday_str}&birth_time={birth_time_str}&sex={sex}')
    else:
        form = FengShuiFortuneForm()

    breadcrumb_data = [
        {'title': 'Trang chủ', 'href': '/'},
        {'title': 'Sim phong thuỷ', 'href': ''},
    ]
    context = {
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'tenant': tenant,
        'breadcrumb_data': breadcrumb_data,
        'form': form,
    }

    if page:
        context['page'] = page
        context['tenant'] = tenant
        context['content'] = parse_content(html.unescape(page.body), context)
        context['relatedPages'] = relatedPages(page.related_pages)

    context['seo'] = getSeo(page, tenant, context)
    return render(request, f"{tenant.theme_folder}/fengShuiFortune.html", context)

@cache_page(60 * 15)
def orderSimRequiredPage(request):
    tenant = request.tenant
    page = ArticlePage.pageManager.filter(slug=f'dat-sim-theo-yeu-cau').first()
    breadcrumb_data = [
        {'title': 'Trang chủ', 'href': '/'},
        {'title': 'Đặt sim theo yêu cầu', 'href': ''},
    ]
    context = {
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'tenant': tenant,
        'breadcrumb_data': breadcrumb_data
    }
    if page:
        context['content'] = parse_content(html.unescape(page.body), context)
    context['seo'] = getSeo(page, tenant, context)
    telco = request.POST.get('telco', '')
    number_nice = request.POST.get('number_nice', '')
    price = request.POST.get('price', '')
    notes = request.POST.get('notes', '')
    other_option = "Nhà mạng: " + str(telco) + "\n" + "Kiểu số đẹp: " + str(number_nice) + "\n" + "Khoảng giá: " + str(price) + "\n" + "Ghi chú: " + str(notes)
    required_fields = ['name', 'phone']
    if request.method == 'POST' and all(request.POST.get(field) for field in required_fields):
        try:
            sim_order = SimOrder.objects.create(
                name=request.POST.get('name'),
                phone=request.POST.get('phone'),
                order_type=REQUEST_CHOICES.REQUEST,
                pushed=0,
                other_option=other_option,
                source_text = remove_www(request.get_host().split(':')[0]),
                store_type = STORE_TYPES.KHO_SIM,
             )
            return redirect(f'{reverse("sims:passSimRequiredPage")}?code={sim_order.code}')
        except ValidationError as e:
            pass  
    return render(request, f'{tenant.theme_folder}/orderSimRequired.html', context)


def passSimRequiredPage(request):
    tenant = request.tenant
    code = request.GET.get('code')
    sim = get_object_or_404(SimOrder, code=code, order_type=REQUEST_CHOICES.REQUEST)
    host = request.get_host()
    disable_sidebar_article = True
    context = {
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'sim': sim,
        'tenant': tenant,
        'host': host,
        'disable_sidebar_article': True,
    }
    page = ArticlePage.pageManager.filter(slug="yeu-cau-thanh-cong").first()
    if page:
        context['page'] = page
        context['tenant'] = tenant
        context['content'] = parse_content(html.unescape(page.body), context)
        context['seo'] = getSeo(page, tenant, context)
    return render(request, f'{tenant.theme_folder}/blog/page.html', context)

@cache_page(60 * 15)
def sim_valuation(request):
    tenant = request.tenant
    simNumber = request.GET.get('sim', '')
    data = getSimValuation(simNumber, tenant)
    price = None
    if simNumber:
        price = data["valuation"][simNumber]
    page = ArticlePage.pageManager.filter(slug=f'dinh-gia-sim').first()
    breadcrumb_data = [
        {'title': 'Trang chủ', 'href': '/'},
        {'title': 'Định giá sim', 'href': ''},
    ]
    context = {
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'sim': simNumber,
        'price': price,
        'tenant': tenant,
        'breadcrumb_data': breadcrumb_data
    }
    if page:
        context['page'] = page
        context['tenant'] = tenant
        context['content'] = parse_content(html.unescape(page.body), context)  
        context['seo'] = getSeo(page, tenant, context)
    return render(request, f'{tenant.theme_folder}/sim_valuation.html', context)


