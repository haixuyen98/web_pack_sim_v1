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

@admin.action(description="Xoá các số đã chọn")
def delete_sim_store(modeladmin, request, queryset):
    if 'apply' in request.POST:
        try:
            modeladmin.model.objects.filter(id__in=queryset).update(d=True)
            messages.success(request, "Đã xóa thành công !!!")
        except Exception as e:
            print("An error occurred:", str(e))
            messages.error(request, "Xóa số thất bại !!!")
        return HttpResponseRedirect(request.get_full_path())
    else:
        context = {
            **modeladmin.admin_site.each_context(request),
            "title": "Xác nhận xóa",
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
            "sims": queryset,
        }
        return TemplateResponse(request, "admin/sims/simstore/delete_sim_store_confirmation.html", context)


@admin.action(description="Ẩn các số đã chọn")
def hide_sim_store(modeladmin, request, queryset):
    try:
        models.SimStore.objects.filter(id__in=queryset).update(h=True)
        messages.success(request, "Đã ẩn thành công !!!")
    except Exception as e:
        print("An error occurred:", str(e))
        messages.error(request, "Ẩn số thất bại !!!")

@admin.action(description="Hiển thị các số đã chọn")
def show_sim_store(modeladmin, request, queryset):
    try:
        models.SimStore.objects.filter(id__in=queryset).update(h=False)
        messages.success(request, "Đã hiển thị thành công !!!")
    except Exception as e:
        print("An error occurred:", str(e))
        messages.error(request, "Hiển thị số thất bại !!!")