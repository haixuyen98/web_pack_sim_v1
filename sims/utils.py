import requests
import json
from core.helpers import get_current_tenant
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile
from .common.choices import STATUS_PAY_CHOICES, STATUS_AR_CHOICES, REQUEST_CHOICES, TYPE_AR_CHOICES
from django.db.models import Sum
from .models import AccountReceivable, SimOrder
from banking_affiliate.models import Transaction
from banking_affiliate.constants import TRANS_STATUS_CHOICES
from django.utils import timezone
from django.db.models import Q

# chu y ham nay cung duoc goi tu function callback_after_payment_statement ben mb,
# neu thay doi tham so webhook thi cung chinh lai các tham số truyền sang từ callback_after_payment_statement
def push_order_to_webhook(order):
    order_info = None
    tenant = get_current_tenant()
    if isinstance(order, SimOrder):
        order_info = {attr_name: getattr(order, attr_name) for attr_name in vars(order)}
        keeping_fee= order.attributes.get("prepay", 0)
        payment_on_delivery= order.attributes.get("payment_on_delivery", 0)
        order_info['keeping_fee'] = keeping_fee
        order_info['payment_on_delivery'] = payment_on_delivery
        if order.order_type == REQUEST_CHOICES.REQUEST:
            order_info['is_request'] = True
    elif isinstance(order, dict):
        order_info = {attr_name: order[attr_name] for attr_name in order}
    # push order to each webhook url in the list
    for url in tenant.config['webhook_list_url']:
        webhook_url = url['webhook_url'].strip()
        format_content = url["content"]
        content = json.loads(format_content.format(**order_info))
        try:
            if url['uuid'] == '01appsim' and 'appsim_account' in tenant.config:
                appsim_content = {
                    'user_id': tenant.config['appsim_account']['appsim_user_id'],
                    'common_type': 40,
                    'send_sms': False,
                }
                content = {**appsim_content, **json.loads(format_content.format(**order_info))}
            else:
                content = json.loads(format_content.format(**order_info))
            response = requests.post(webhook_url, json=content)
            response.raise_for_status()
            # change viewed status to True
            if response.status_code == 200:
                if isinstance(order, SimOrder):
                    order.pushed = True
                    order.save()
        except requests.exceptions.RequestException as e:
            print(f"Webhook request failed: {e}")

def assignOrderToSale(order):
    try:
        current_user = User.objects.filter(is_staff=True, userprofile__assign_order=True, userprofile__is_current_assign=True).order_by('id').last()
        if not current_user:
            raise ObjectDoesNotExist("User does not exist.")
        next_record = User.objects.filter(is_staff=True, userprofile__assign_order=True, id__gt=current_user.id).order_by('id').first()
        if not next_record:
            raise ObjectDoesNotExist("User does not exist.")
    except ObjectDoesNotExist:
        next_record = User.objects.filter(is_staff=True, userprofile__assign_order=True).order_by('id').first()
        
    if next_record:
        order.sale_pic = next_record
        order.save()
        # update older current assign to False
        users_with_assign = User.objects.filter(userprofile__is_current_assign=True)
        user_profiles = UserProfile.objects.filter(user__in=users_with_assign)
        user_profiles.update(is_current_assign=False)
        # User.objects.filter(userprofile__is_current_assign=True).update(userprofile__is_current_assign=False)
        # update current assign to True
        next_record.userprofile.is_current_assign = True
        next_record.userprofile.save()
def check_order_exist_ago(sim):
    minutes_ago = timezone.now() - timezone.timedelta(minutes=7200) # 5 ngay
    order = SimOrder.objects.filter(Q(createdAt__gte=minutes_ago) & Q(sim=sim)).first()
    return order
def check_trans_mb_exist_ago(sim):
    minutes_ago = timezone.now() - timezone.timedelta(minutes=7200) # 5 ngay
    trans = Transaction.objects.filter(Q(createdAt__gte=minutes_ago) & Q(sim=sim) & Q(status=TRANS_STATUS_CHOICES.PAID)).first()
    return trans
# cap that trang thai thanh toan theo tong tien thanh toan
def update_payment_status(order):
    # chi cap nhat neu pay_kh_status != Thanh toan (CHO KH)
    change = False
    if order and order.pay_kh_status!=STATUS_PAY_CHOICES.PAID:
        # don thuong
        if order.order_type == REQUEST_CHOICES.COMMON:
            total_amount = AccountReceivable.objects.filter(type=TYPE_AR_CHOICES.KH, status=STATUS_AR_CHOICES.PAID, sim_order__code=order.code).aggregate(Sum('amount_payment'), Sum('amount_interest'))
            total_amount_payment = total_amount['amount_payment__sum']
            total_amount_interest = total_amount['amount_interest__sum']
            if total_amount_payment is None:
                total_amount_payment = 0
            if total_amount_interest is None:
                total_amount_interest = 0
            # total_amount_payment_interest = total_amount_payment + total_amount_interest
            if total_amount_payment>=order.amount:
                order.pay_kh_status = STATUS_PAY_CHOICES.PAID
                change = True
            elif total_amount_payment>0 and total_amount_payment<order.amount:
                order.pay_kh_status = STATUS_PAY_CHOICES.PAIDING
                change = True
        # don tra gop
        elif order.order_type == REQUEST_CHOICES.INSTALLMENT:
            total_amount = AccountReceivable.objects.filter(type=TYPE_AR_CHOICES.KH, status=STATUS_AR_CHOICES.PAID, sim_order__code=order.code).aggregate(Sum('amount_payment'), Sum('amount_interest'))
            total_amount_payment = total_amount['amount_payment__sum']
            total_amount_interest = total_amount['amount_interest__sum']
            if total_amount_payment is None:
                total_amount_payment = 0
            if total_amount_interest is None:
                total_amount_interest = 0
            # total_amount_payment_interest = total_amount_payment + total_amount_interest
            if total_amount_payment>=order.amount:
                order.pay_kh_status = STATUS_PAY_CHOICES.PAID
                change = True
            elif total_amount_payment>0 and total_amount_payment<order.amount:
                order.pay_kh_status = STATUS_PAY_CHOICES.PAIDING
                change = True
    # chi cap nhat neu pay_tho_status != Thanh toan (CHO THO)
    if order and order.pay_tho_status!=STATUS_PAY_CHOICES.PAID:
        # don thuong
        if order.order_type == REQUEST_CHOICES.COMMON:
            total_amount = AccountReceivable.objects.filter(type=TYPE_AR_CHOICES.THO, status=STATUS_AR_CHOICES.PAID, sim_order__code=order.code).aggregate(Sum('amount_payment'), Sum('amount_interest'))
            total_amount_payment = total_amount['amount_payment__sum']
            total_amount_interest = total_amount['amount_interest__sum']
            if total_amount_payment is None:
                total_amount_payment = 0
            if total_amount_interest is None:
                total_amount_interest = 0
            # total_amount_payment_interest = total_amount_payment + total_amount_interest
            if total_amount_payment>=order.amount:
                order.pay_tho_status = STATUS_PAY_CHOICES.PAID
                change= True
            elif total_amount_payment>0 and total_amount_payment<order.amount:
                order.pay_tho_status = STATUS_PAY_CHOICES.PAIDING
                change = True
        # don tra gop
        elif order.order_type == REQUEST_CHOICES.INSTALLMENT:
            total_amount = AccountReceivable.objects.filter(type=TYPE_AR_CHOICES.THO, status=STATUS_AR_CHOICES.PAID, sim_order__code=order.code).aggregate(Sum('amount_payment'), Sum('amount_interest'))
            total_amount_payment = total_amount['amount_payment__sum']
            total_amount_interest = total_amount['amount_interest__sum']
            if total_amount_payment is None:
                total_amount_payment = 0
            if total_amount_interest is None:
                total_amount_interest = 0
            # total_amount_payment_interest = total_amount_payment + total_amount_interest
            if total_amount_payment>=order.amount:
                order.pay_tho_status = STATUS_PAY_CHOICES.PAID
                change = True
            elif total_amount_payment>0 and total_amount_payment<order.amount:
                order.pay_tho_status = STATUS_PAY_CHOICES.PAIDING
                change = True
    if change:
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        order.save()