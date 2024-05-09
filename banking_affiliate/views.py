from django.http import JsonResponse
import requests
from .constants import createTransactionEndpoint, SOURCE_CHOICES,TRANS_STATUS_CHOICES, MY_WEBHOOK_TOKEN
from sims.common.choices import REQUEST_CHOICES, STORE_TYPES
from .models import Transaction, Customer
from sims.services.sim_service import getSimDetail
import json
from django.shortcuts import redirect, render
from django.urls import reverse
from .helpers import b64encode, getKeepingFee
from django.views.decorators.csrf import csrf_exempt
from sims.models import SimOrder
from sims.common.choices import STATUS_PAY_CHOICES, STATUS_CHOICES
from blog.models import ArticlePage
from sims.services.helpers import getSeo, parse_content
from .helpers import get_mb_user_info
import html
from django.db.models import Q
from django.utils import timezone
from sims.utils import push_order_to_webhook
from core.helpers import decrypt_data, encrypt_data
import os
from datetime import datetime, timedelta

MB_BANK_TRANSACTION_TYPE = 'mb'
# Create your views here.
# ham nay de FE lay ve thong tin transaction de check success sau khi sau khi orderPlace ok
def get_transaction_info(request):
    transactionId = request.GET.get('transactionId')
    config = request.tenant.config
    mb_bank_base_api = config.get("mb_bank_base_api", None)
    mb_bank_merchant_secret = config.get("mb_bank_merchant_secret", None)
    mb_bank_merchant_code = config.get("mb_bank_merchant_code", None)
    allow_sale_via_bank = config.get("allow_sale_via_bank", 'off')
    headers = {
        'Content-Type': 'application/json',
        'MERCHANT_CODE': mb_bank_merchant_code,
        'MERCHANT_SECRET': mb_bank_merchant_secret,
    }
    data = {
        'code': 401,
        'success': False,
        'message': 'Failure',
        'transaction': [],
    }
    if mb_bank_base_api:
        transaction_url = f"{mb_bank_base_api}{createTransactionEndpoint}/{transactionId}"
        response = requests.get(transaction_url, headers=headers, data=[])
        json_data = response.json()
        if response.status_code == 200:
            data = {
                'code': json_data['code'],
                'success': True,
                'message': 'Success',
                'transaction': response.json(),
		    }
        else:
            data = {
                'code': json_data['code'],
                'success': False,
                'message': json_data['error_code'],
                'transaction': [],
		    }
    else:
        data = {
        'code': 401,
        'success': False,
        'message': 'not allow_sale_via_bank or blank mb_bank_base_api',
        'transaction': [],
    }
    return JsonResponse(data)

@csrf_exempt
def get_user_info(request):
    login_token = request.GET.get('loginToken')
    data = {
        'code': 401,
        'success': False,
        'message': 'Failure',
        'user': None,
    }
    json_data = get_mb_user_info(login_token,request.tenant)  
    if json_data:
        secret_key = normalize_key_length(os.environ.get('SECRET_KEY', "data12kldsfjlsd!@31"))
        try:
            customer = Customer.objects.get(cif=f"{json_data['cif']}")
            customer.sessionId = json_data['sessionId']
            customer.login_token= login_token
            customer.save()
            data = {
                'code': 200,
                'success': True,
                'message': 'Success',
                'user': json_data,
                'mb_user_sessionId': encrypt_data(json_data['sessionId'], secret_key),
                'mb_user_cif': encrypt_data(json_data['cif'], secret_key),
                'mb_user_name': encrypt_data(json_data['fullname'], secret_key),
                'mb_user_phone': encrypt_data(json_data['mobile'], secret_key),
            }
        except:
            customer = Customer.objects.create(
                cif = json_data['cif'],
                sessionId = json_data['sessionId'],
                fullname = json_data['fullname'],
                mobile = json_data['mobile'],
                login_token= login_token,
                source = SOURCE_CHOICES.MB
            )
            data = {
                'code': 200,
                'success': True,
                'message': 'Success',
                'user': json_data,
                'mb_user_sessionId': encrypt_data(json_data['sessionId'], secret_key),
                'mb_user_cif': encrypt_data(json_data['cif'], secret_key),
                'mb_user_name': encrypt_data(json_data['fullname'], secret_key),
                'mb_user_phone': encrypt_data(json_data['mobile'], secret_key),
            }
            print(f"get_user_info not found customer with cif {json_data['cif']}")
    else:
        data = {
        'code': 401,
        'success': False,
        'message': 'not allow_sale_via_bank or blank mb_bank_base_api',
        'user': None,
    }
    return JsonResponse(data)

def create_mb_transaction(request, order_data):
    config = request.tenant.config
    secret_key = normalize_key_length(os.environ.get('SECRET_KEY', "data12kldsfjlsd!@31"))
    mb_bank_transaction_type = config.get("mb_bank_transaction_type", MB_BANK_TRANSACTION_TYPE)
    mb_bank_base_api = config.get("mb_bank_base_api", None)
    mb_bank_merchant_secret = config.get("mb_bank_merchant_secret", None)
    mb_bank_merchant_code = config.get("mb_bank_merchant_code", None)
    mb_user_sessionId = decrypt_data(request.COOKIES.get('mb_user_sessionId'),secret_key)
    mb_user_cif = decrypt_data(request.COOKIES.get('mb_user_cif'),secret_key)
    bodyContent             = {
        'sessionId'    : mb_user_sessionId,
        'allowCard'    : False,
        'cif'          : mb_user_cif,
        'amount'        : order_data['amount'],
        'description'  : f"Đặt mua sim {order_data['sim']}",
        'type'          : mb_bank_transaction_type,
        'successMessage': '',
        'metadata'     : f"telco_text={order_data['telco_text']}",
        # 'address'       : order_data['address'] if order_data['address'] else '',
        # 'price'         : order_data['price_calc'],
    }
    if 'prepay' in order_data and order_data['prepay']:
        bodyContent['description'] = f"Phí giữ sim {order_data['sim']}"

    transaction_url = f"{mb_bank_base_api}{createTransactionEndpoint}"
    headers = {
        'Content-Type': 'application/json',
        'MERCHANT_CODE': mb_bank_merchant_code,
        'MERCHANT_SECRET': mb_bank_merchant_secret,
    }
    # $user = User::find()->where(['session_id' => $bodyContent['sessionId']])->one();
    customer = Customer.objects.filter(sessionId=bodyContent['sessionId']).first()
    if customer:
        bodyContent['cif'] = customer.cif
        response = requests.post(transaction_url, headers=headers, json=bodyContent)
        
        if response.status_code==200:
            # chuyển trạng thái các record khác cùng phone + sim
            del order_data['csrfmiddlewaretoken']
            Transaction.objects.filter(sim=order_data['sim'], phone=order_data['phone'], status=TRANS_STATUS_CHOICES.PENDING).update(status=TRANS_STATUS_CHOICES.DELETED)
            payment_request = response.json()
            client_ip = request.META.get('REMOTE_ADDR')
            prepay  = order_data['prepay'] if 'prepay' in order_data else 0
            payment_on_delivery= order_data['payment_on_delivery'] if 'payment_on_delivery' in order_data else 0
            payment_request['description'] += f" giá gốc {int(order_data['price'])}, giá bán {int(order_data['price_calc'])}"
            
            if prepay:
                payment_request['description'] += f" thanh toán trước {int(prepay)}"
            if payment_on_delivery:
                payment_request['description'] += f" còn lại {int(payment_on_delivery)}"
            
            transaction = Transaction.objects.create(
                transaction_code= payment_request['id'], # check lai field nay
                sim= order_data['sim'],
                amount= order_data['amount'],
                cif= customer.cif,
                description= payment_request['description'], 
                merchant= payment_request['merchant']['code'],
                status = payment_request['status'],
                address = order_data['address'] if order_data['address'] else '',
                name = order_data['name'],
                phone  = order_data['phone'],
                source  = SOURCE_CHOICES.MB,
                session_id  = bodyContent['sessionId'],
                sim_full = order_data['sim'],
                ip=client_ip,
                sim_info = json.dumps(order_data),
                prepay=prepay,
                price= order_data['price'],
                price_calc= order_data['price_calc'],
                payment_on_delivery= payment_on_delivery,
                user_id = customer.id,
                attributes={
                    'telco_text': order_data['telco_text']
                },
                browse_history= order_data['browse_history'] if 'browse_history' in order_data else "",
            )
            return {
                'code': 200,
                'transaction': transaction
            }
    else:
        return {
            'code': 400,
            'message': 'Có lỗi xảy ra trong quá trình đặt mua sản phẩm'
        }  
# webhook gui mb_pedning with transaction time < 10 minutes
@csrf_exempt
def push_mb_pending_topsim_webhook(request, token):
    if token == MY_WEBHOOK_TOKEN:
        # lay ra danh sach don hang trong vong 5 ngay, voi transaction_code not null
        five_day_ago = datetime.now() - timedelta(days=5)
        transaction_codes = SimOrder.objects.filter(
            createdAt__gte=five_day_ago,
            attributes__transaction_code__isnull=False
        ).values_list('attributes__transaction_code', flat=True)
        transaction_codes_list = list(transaction_codes)
        
        # quet all transaction duoc tao sau 10 phut ma trang thai van PENDING
        # va khong nam trong danh sach order da thanh toan 
        # chi lay 1 ban ghi sim theo sdt khach hang (phone) va chuyen tat ca cac transaction tren sang trang thai push
        ten_minutes_ago = timezone.now() - timezone.timedelta(minutes=120)
        transactions = Transaction.objects.exclude(
            transaction_code__in=transaction_codes_list
        ).filter(
            Q(status=TRANS_STATUS_CHOICES.PENDING) & Q(createdAt__lte=ten_minutes_ago) & Q(createdAt__gte=five_day_ago)
        ).distinct('sim', 'phone')
        # transactions_list = list(transactions.values())
        # push danh sach pending nay sang ben topsim
        for trans in transactions:
            order = {
                "name": trans.name,
                "phone": trans.phone,
                "sim": trans.sim,
                "amount": trans.amount,
                "address": trans.address,
                "source_text": 'mb_pending',
                "other_option": str(trans.price) + " mp_pending",
                "createdAt": trans.createdAt,
                "search_history": "",
                "ip": trans.ip,
                "order_type": "",
            }
            push_order_to_webhook(order)
            trans.status = TRANS_STATUS_CHOICES.PUSH_PENDING
            trans.save()
        return JsonResponse({
            'code': 200,
            'success': True,
            'message': 'push success'
        })

    else:
        return JsonResponse({
            'code': 400,
            'success': False,
            'message': 'token invalid'
        })
        
@csrf_exempt
def callback_after_payment_statement(request):
    token = request.GET.get('token', '')
    print("request.body", request.body)
    if token == MY_WEBHOOK_TOKEN:
        config = request.tenant.config
        mb_bank_merchant_code = config.get("mb_bank_merchant_code", None)
        mb_bank_transaction_type = config.get("mb_bank_transaction_type", MB_BANK_TRANSACTION_TYPE)
        mb_bank_check_sum_secret = config.get("mb_bank_check_sum_secret", None)
        
        mb_order_data = json.loads(request.body)
        transactionId = mb_order_data['id'] if 'id' in mb_order_data else ''
        cif           = mb_order_data['cif'] if 'cif' in mb_order_data else ''
        status        = mb_order_data['status'] if 'status' in mb_order_data else ''
        amount        = mb_order_data['amount'] if 'amount' in mb_order_data else ''
        status        = mb_order_data['status'] if 'status' in mb_order_data else ''
        checksum      = mb_order_data['checksum'] if 'checksum' in mb_order_data else ''
        encodeString  = f"{mb_bank_merchant_code}{transactionId}{mb_bank_transaction_type}{cif}{amount}{status}"
        sig = b64encode(encodeString, mb_bank_check_sum_secret)
        
        if transactionId and cif and sig == checksum:
        # if transactionId and cif:
            # update transaction, lay transaction đã ở trang thái thanh toán
            transaction = Transaction.objects.filter(
                Q(transaction_code=transactionId) & ~Q(status=TRANS_STATUS_CHOICES.PAID) & Q(cif=cif)
            ).first()
            if transaction:
                transaction.status = status
                transaction.save()
                if transaction.isCompleted():
                    SimOrder.objects.create(
                        sim=transaction.sim,
                        phone=transaction.phone,
                        amount=transaction.price_calc,
                        order_type=REQUEST_CHOICES.COMMON,
                        name=transaction.name,
                        address=transaction.address,
                        other_option= transaction.description,
                        ip= transaction.ip,
                        pushed=False,
                        store_type=STORE_TYPES.KHO_APPSIM,
                        source_text = SOURCE_CHOICES.MB,
                        status = STATUS_CHOICES.PROCESSING,
                        pay_kh_status= STATUS_PAY_CHOICES.PAID,
                        pay_tho_status=STATUS_PAY_CHOICES.UN_PAIDED,
                        attributes={
                            'prepay': str(transaction.prepay),
                            'payment_on_delivery': str(transaction.payment_on_delivery),
                            'price_origin': str(transaction.price),
                            'transaction_code': transaction.transaction_code,
                            'user_id': transaction.user_id,
                            'cif': transaction.cif,
                            'session_id': transaction.session_id,
                            'telco_text': transaction.attributes['telco_text'],
                            'keeping_fee': 0,
                            'payment_on_delivery': 0,
                            'order_type': REQUEST_CHOICES.COMMON
                        },
                        browse_history = transaction.browse_history,
                    )
                    return JsonResponse({
                        'code': 200,
                        'message': 'transaction successful',
                    })
                else:
                    return JsonResponse({
                        'code': 400,
                        'message': 'transaction is not completed',
                    })
        return JsonResponse({
            'code': 400,
            'message': 'transaction not found'
        })
    else:
        return JsonResponse({
            'code': 401,
            'message': 'Not Authorized'
        })
    
def normalize_key_length(secret_key):
    # Nếu độ dài của secret_key nhỏ hơn 32 bytes, thêm ký tự '0' cho đến khi đủ
    while len(secret_key) < 32:
        secret_key += '0'
    # Trả về 32 bytes đầu tiên của secret_key
    return secret_key[:32]

# ham xu ly khi ng dung click submit form
def submitSimOrder(request, sim):
    tenant = request.tenant
    required_fields = ['name', 'phone']
    sim_keeping_percent = tenant.config.get('sim_keeping_percent', '0')
    order_data = request.POST.dict()
    order_data['sim'] = sim
    sim_data = getSimDetail(sim, tenant)
    if request.method == 'POST' and all(request.POST.get(field) for field in required_fields):
        if sim_data:
            minutes_ago = timezone.now() - timezone.timedelta(minutes=7200) # 5 ngay
            # kiem tra xem sim nay co ai mua da thanh toan 5 ngay truoc ko
            transaction = Transaction.objects.filter(
                    Q(sim=sim) &
                    Q(status=TRANS_STATUS_CHOICES.PAID) & Q(createdAt__gte=minutes_ago)
                ).first()
            if not transaction:
                order_data['t'] = sim_data['t']
                order_data['amount'] = sim_data['price_calc']
                order_data['price'] = sim_data['price']
                order_data['price_calc'] = sim_data['price_calc']
                order_data['telco_text'] = sim_data['telcoText']
                # neu kh chon giu sim
                type_submit = order_data.get('type_submit')
                if type_submit and order_data['type_submit'] == 'keep_sim':
                    order_data['amount'] = getKeepingFee(sim_data['price_calc'], sim_keeping_percent)
                    order_data['prepay'] = order_data['amount']
                    order_data['payment_on_delivery'] = sim_data['price_calc'] - order_data['amount']
                transaction_response = create_mb_transaction(request, order_data)
                
                if transaction_response['code'] ==200:
                    transaction = transaction_response['transaction']
                    print("transaction transaction", transaction)
                    # return redirect(f"{reverse('banking_affiliate:banking_statement_waiting')}?cif={transaction.cif}&transaction_code={transaction.transaction_code}")
                    response = redirect(f"{reverse('banking_affiliate:banking_statement_waiting')}")
                    secret_key = normalize_key_length(os.environ.get('SECRET_KEY', "data12kldsfjlsd!@31"))
                    response.set_cookie('transaction_code', encrypt_data(transaction.transaction_code, secret_key), max_age=600)
                    response.set_cookie('transaction_cif', encrypt_data(transaction.cif, secret_key), max_age=600)
                    return response
            else:
                return redirect(f"{reverse('sims:failSimOrderPage')}?sim={sim}&error=order_duplicate")
    return redirect(f"{reverse('sims:failSimOrderPage')}?sim={sim}&error=bad-request")
# khi vao page nay se mo popup de thanh toan, neu KH thanh toan xong, MB se tu redirect sang link thanh cong callback_after_bank_successful
def banking_statement_waiting(request):
    tenant = request.tenant
    config = request.tenant.config
    mb_bank_transaction_type = config.get("mb_bank_transaction_type", MB_BANK_TRANSACTION_TYPE)
    mb_bank_merchant_code = config.get("mb_bank_merchant_code", None)
    
    secret_key = normalize_key_length(os.environ.get('SECRET_KEY', "data12kldsfjlsd!@31"))
    transaction_code = decrypt_data(request.COOKIES.get('transaction_code',''), secret_key)
    cif = decrypt_data(request.COOKIES.get('transaction_cif',''), secret_key)
    transaction = Transaction.objects.filter(transaction_code=transaction_code, cif=cif).first()
    print("transaction", transaction)
    if transaction:
        context = {
            'transaction': json.dumps({
                'amount': float(transaction.amount),
                'cif': transaction.cif,
                'transaction_code': transaction.transaction_code,
                'description': transaction.description,
                'status': transaction.status
            }),
            'mb_bank_merchant_code': mb_bank_merchant_code,
            'mb_bank_transaction_type':mb_bank_transaction_type,
            'tenant': tenant,
        }
        print("context", context)
        response = render(request, f'{tenant.theme_folder}/sim_banking_statement_waiting.html', context)
        response.set_cookie('transaction_code', transaction.transaction_code)
        return response
    else:
        return redirect(f"{reverse('sims:failSimOrderPage')}?sim={transaction.sim}&error=bad-request")
# function callback from bank sau khi thanh toan thanh cong
def callback_after_bank_successful(request):
    tenant = request.tenant
    login_token = request.GET.get("loginToken", None)
    user_info = get_mb_user_info(login_token, tenant)
    context = {
        'request': request,
        'theme_folder': tenant.theme_folder,
        'theme_config': tenant.theme_config,
        'tenant': tenant
    }
    if user_info:
        transaction = Transaction.objects.filter(cif=user_info['cif']).order_by("-createdAt").first()
        if transaction:
            order = SimOrder.objects.filter(attributes__contains={"transaction_code":transaction.transaction_code}).first()
            context['order'] = order
            context['telco_text'] = order.attributes.get('telco_text','')
            page = ArticlePage.pageManager.filter(slug="mb-dat-sim-thanh-cong").first()
            if page:
                context['page'] = page
                context['content'] = parse_content(html.unescape(page.body), context)
                context['seo'] = getSeo(page, tenant, context)
    return render(request, f'{tenant.theme_folder}/blog/page.html', context)
