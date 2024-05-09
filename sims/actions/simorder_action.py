from django.contrib import admin
from django.template.response import TemplateResponse
from django.contrib.admin.utils import model_ngettext
from django.contrib.auth.models import User
from django.template.response import TemplateResponse
from sims.forms import SimOrderStatusChangeForm
from .. import models
from django.contrib import messages
from django.http import HttpResponseRedirect
from ..utils import push_order_to_webhook

@admin.action(description="Đẩy vào webhook")
def pushwebhook_order_action(modeladmin, request, queryset):
    #if request.POST.get('post'):
    for order in queryset:
        if not order.pushed:
            messages.success(request, f"Đơn hàng {order.code} với sim {order.sim} thành công gửi tới webhook.")
            push_order_to_webhook(order)
        else:
            messages.warning(request, f"Đơn hàng {order.code} với sim {order.sim} đã được gửi tới webhook trước đó.")

@admin.action(description="Phân công người phụ trách")
def assign_order_to_pic_action(modeladmin, request, queryset):
    if 'apply' in request.POST:
        selected = request.POST.get('_selected_action')
        # Retrieve selected order IDs
        # Convert the comma-separated string to a list of integers
        order_ids = [int(id) for id in request.POST.get('orders', '').split(',')]
        if selected and order_ids:
            user_id = int(selected)
            selected_user = User.objects.get(id=user_id)
            # Retrieve the order objects using the preserved order IDs
            selected_orders = modeladmin.model.objects.filter(id__in=order_ids)
            
            # Update the sale_pic field for each selected order
            selected_orders.update(sale_pic=selected_user)

            messages.success(request, f"Các đơn hàng được chọn đã được chuyển cho {selected_user.username} thành công.")
            return HttpResponseRedirect(request.get_full_path())
    else:
        users = User.objects.all()
        context = {
            **modeladmin.admin_site.each_context(request),
            "title": "Chỉ định",
            "orders": queryset,
            "users": users,
        }
        return TemplateResponse(request, "admin/sims/simorder/assign_to_sale_pic.html", context)
