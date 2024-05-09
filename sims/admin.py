from django.contrib import admin
import json
# Register your models here.
from . import models
from django.urls import reverse, path
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .sim_detect.detect_pack import detectPack
from .sim_detect.detect_home_network import detectTelco, getTelcoInput
from .sim_detect.detect_cate import get_cat_id
from django.utils import timezone
from sims.services.helpers import vn_date_format
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html, escape
from django.template.response import TemplateResponse
from sims.forms import SimOrderStatusChangeForm, SimOrderSaleNotesChangeForm, SimOrderAdminForm, SimStoreAdminForm, SimStoreCommentsChangeForm
from .filters.simorder_filter import CustomCreatedAtFilter, CustomPushedFilter
from .filters.simstore_filter import CustomPublishFilter, CustomPackFilter, CustomStatusFilter, CustomCateFilter, CustomPriceFilter
from .actions.simorder_action import pushwebhook_order_action, assign_order_to_pic_action
from .actions.simstore_action import delete_sim_store, hide_sim_store, show_sim_store
from core.helpers import formatCurrency
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from tenant.admin import CustomUserAdmin as AuthUserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from sims.forms import ArticlePageSimConfigAdminForm
from blog.models import ArticlePage, Article
from django.db.models import Q
from .services.helpers import getSimUrlFilter
from .services.sim_service import _getQueryParam
from sims.common.choices import PAY_METHOD_CHOICES, STORE_TYPES, STATUS_AR_CHOICES, REQUEST_CHOICES, STATUS_PAY_CHOICES, get_label_from_value
from sims.services.sim_service import getSims, getSellerInfo, getPhoneInfo, getSimDetail
from sims.services.helpers import getSimUrlFilter
import re
from django.db import transaction
from openpyxl import Workbook
from django import forms
from django.template import loader
from django.contrib.admin.views.main import ChangeList
from blog.widget import CustomHTMLSlug
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from .utils import update_payment_status
from core.helpers import autoClearCache
from sims.common.choices import (
    NHA_MANG_CHOICES,
    CATEGORY_CHOICES,
    PACK_CHOICES,
    INSTALLMENT_PAYMENT_CHOICES,
    INSTALLMENT_TERM_CHOICES,
    INSTALLMENT_TYPE_CHOICES,
    STORE_TYPES,
    STATUS_CHOICES,
    TYPE_AR_CHOICES,
    REQUEST_CHOICES,
)

class CustomChangeList(ChangeList):
    def get_results(self, request):
        result_count = models.SimStore.objects.filter(d=False).count()
        super().get_results(request)
        self.full_result_count = result_count

class CustomHTMLMultiSelectWidget(forms.Widget):
    template_name = 'admin/sims/simstore/components/customize_multiselect.html'
    def __init__(self, choices=(), attrs=None, *args, **kwargs):
        super().__init__(attrs, *args, **kwargs)
        self.choices = choices

    def render(self, name, value, attrs=None, renderer=None):
        template = loader.get_template(self.template_name)
        context = {
            'name': name,
            'id': f'id_{name}',
            'value': [int(x) for x in value.split(",")] if value else [],
            'choices': self.choices,
        }
        return template.render(context)

    def value_from_datadict(self, data, files, name):
        return data.getlist(name)

@admin.register(models.SimStore)
class SimStoreAdmin(admin.ModelAdmin):
    form = SimStoreAdminForm
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'ip' in form.base_fields:
            form.base_fields['ip'].widget = CustomHTMLMultiSelectWidget(choices=INSTALLMENT_PAYMENT_CHOICES)
        if 'it' in form.base_fields:
            form.base_fields['it'].widget = CustomHTMLMultiSelectWidget(choices=INSTALLMENT_TERM_CHOICES)
        return form

    list_display = ('f', 'custom_pb_format', 'display_c', 'c2', 'display_t', 'display_tt', 'display_installment_info', 'note', 'display_h', 'publish', 'comments_display')
    search_fields = ['id']
    list_filter = (CustomPriceFilter, CustomCateFilter,'t', CustomPackFilter, CustomStatusFilter, CustomPublishFilter)
    empty_value_display=""
    ordering=['-publish']
    actions = [delete_sim_store, hide_sim_store, show_sim_store]
    list_per_page = 50

    fieldsets = (
        (_('Số sim'), {
            'fields': ('pb', 't', 'h','tt', 'k', 'ip', 'it', 'iir', 'lpi', 'note')
        }),
    )

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            search_term = re.sub(r'[^0-9*]', '', search_term)
            paramsObj = {
                'q': search_term
            }
            filterObj = getSimUrlFilter("/", paramsObj)
            queryParams = _getQueryParam(filterObj, request.tenant)
            custom_search = (
               queryParams['queryQ'] 
            )
            queryset = queryset.filter(custom_search, d=False)
        else:
            queryset = queryset.filter(d=False)

        return queryset, True

    def get_filtered_queryset(self, request):
        changelist = self.get_changelist_instance(request)
        queryset = changelist.get_queryset(request)
        return queryset

    def export_all_to_excel(self, request):
        queryset = self.get_filtered_queryset(request)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="simstore_data.xlsx"'
        wb = Workbook()
        ws = wb.active
        headers = ['Số sim', 'Giá bán', 'Loại mạng', 'Nhà mạng', 'Ghi chú', 'Thời gian cập nhật']
        ws.append(headers)
        for obj in queryset:
            row = [
                f'{obj.f}',
                f'{obj.pn}',
                f'{obj.excelPackText}',
                f'{obj.telcoText}' ,
                f'{obj.note}' if obj.note else '' ,
                vn_date_format(obj.publish) if obj.publish else '',
            ]

            ws.append(row)
        wb.save(response)
        return response

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "Kho SIM"
    def custom_pb_format(self, obj):
        return format_html('<span style="white-space: nowrap;">{}</span>', obj.pb_format)
    custom_pb_format.short_description = 'Giá bán'

    def display_c(self, obj):
        return ', '.join(obj.get_category_names)
    display_c.short_description = 'Danh mục'

    def display_tt(self, obj):
        return obj.packText
    display_tt.short_description = 'Loại mạng'

    def display_t(self, obj):
        return obj.telcoText
    display_t.short_description = 'Nhà mạng'

    def display_ip(self, ip):
        if ip:
            return ', '.join([f"{value}%" for value in ip])
        return ''

    def display_it(self, it):
        if it:
            return ', '.join([f"{value} tháng" for value in it])
        return ''


    def display_h(self, obj):
        if obj.h:
            return  format_html('<span style="color: red;">{}</span>', 'Đã ẩn')
        return format_html('<span style="color: blue;">{}</span>', 'Đang hiển thị') 

    display_h.short_description = 'Trạng thái'

    def display_iir(self, installment_type, iir):
        if installment_type == INSTALLMENT_TYPE_CHOICES.PERCENT:
            if iir:
                return f'{iir}%/tháng'
        if installment_type == INSTALLMENT_TYPE_CHOICES.VND:
            if iir:
                return f'{iir} đồng/triệu'
        return ''

    def comments_display(self, obj):
        url = reverse('admin:sim_comments_change_action', kwargs={'pk': obj.id})
        truncated_comments = '📝'
        comments_html = ""
        if obj.comment and isinstance(obj.comment, dict):
            for index, comment in obj.comment.items():
                expected_keys = ['commentedBy', 'textComment', 'commentedAt']
                # Check if all expected keys are present in the note
                if all(key in comment for key in expected_keys):
                    username = comment['commentedBy']
                    text_comment = comment['textComment']
                    commentedAt = comment['commentedAt']
                    # Escape HTML to prevent XSS attacks
                    escaped_text_comment = escape(text_comment)
                    # Display each note in the tooltip
                    comments_html += f'<b>{commentedAt} - {username}:</b> {escaped_text_comment}<br/>'
                else:
                    comments_html = ''
        # Truncate the notes to <= 20 chars
        truncated_comments = format_html('<a href="javascript:void(0);" onclick="showPopupModal(\'{}\');" class="editable-field" data-pk="{}" data-field="comment" title="{}">{}</a><br/>',
                    url,
                    truncated_comments,
                    truncated_comments,
                    truncated_comments,
                )
                
        truncated_comments = comments_html  + truncated_comments
        return format_html(truncated_comments)
    comments_display.short_description = 'Comment giữ số'

    def display_installment_info(self, obj):
        if obj.ip and obj.it and obj.installment_type:
            info = format_html(
                'Mua trả góp: {}<br>Thời hạn trả góp: {}<br>Lãi suất trả góp: {}',
                self.display_ip(obj.ip),
                self.display_it(obj.it),
                self.display_iir(obj.installment_type, obj.iir)
            )
            return format_html('<span>{}</span>', info)
        return ''
    display_installment_info.short_description = 'Thông tin trả góp'
    def change_view(self, request, object_id, form_url='', extra_context=None):     
        self.change_form_template = None
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('delete_all/', self.admin_site.admin_view(self.delete_all), name='simstore_delete_all'),
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='simstore_upload_csv'),
            path('export-csv/', self.admin_site.admin_view(self.export_all_to_excel), name='simstore_export_csv'),
            path('change-comments-action/<str:pk>', self.admin_site.admin_view(self.row_comments_action_view),
                 name='sim_comments_change_action'),
            ]
        return new_urls + urls
    def upload_csv(self, request):
        # if request.method == "POST": 
        #     csv_file = request.FILES["csv_upload"]
        #     if not csv_file.name.endswith('.csv'):
        #         messages.warning(request, 'The wrong file type was uploaded')
        #         return HttpResponseRedirect(request.path_info)
        #     file_data = csv_file.read().decode("utf-8")
        #     csv_data = file_data.split("\n")
        #     for x in csv_data:
        #         fields = x.split(",")
        #         created = customer.objects.update_or_create(
        #             name = fields[0],
        #             balance = fields[1],
        #             )
        #     url = reverse('admin:index')
        #     return HttpResponseRedirect(url)
        context = {
            "opts":self.model._meta,
            "title": "Up bảng bằng file",
            "nha_mang_list": NHA_MANG_CHOICES,
            "category_list": CATEGORY_CHOICES,
            "pack_list": PACK_CHOICES,
            "installment_payment": INSTALLMENT_PAYMENT_CHOICES,
            "installment_term": INSTALLMENT_TERM_CHOICES,
            "current_time": int(timezone.now().timestamp()),
            **self.admin_site.each_context(request),
        }

        if request.method == "POST":
            if "submit-form" in request.POST:
                data_form = request.POST
                self.customHandleSubmitForm(request, data_form)
                    
            return HttpResponseRedirect("/admin/sims/simstore")

        return render(request, "admin/sims/simstore/csv_upload.html", context)
    
    def add_view(self, request, extra_context=None):
        total_item = 20
        extra_context = {
            "nha_mang_list": NHA_MANG_CHOICES,
            "range_form": range(total_item),
            "category_list": CATEGORY_CHOICES,
            "pack_list": PACK_CHOICES,
            "installment_payment": INSTALLMENT_PAYMENT_CHOICES,
            "installment_term": INSTALLMENT_TERM_CHOICES,
            "current_time": int(timezone.now().timestamp())
        }
        template_path = f"admin/sims/simstore/add-sim.html"
        self.change_form_template = template_path

        if request.method == "POST":
            if "submit-form" in request.POST:
                data_form = request.POST
                self.customHandleSubmitForm(request, data_form)
            return HttpResponseRedirect("/admin/sims/simstore")
        return super().add_view(request, extra_context=extra_context)

    def customHandleSubmitForm(self, request, data_form):
        data_json = data_form.get('data')
        is_handle_cate = data_form.get('is-handle-cate')
        is_handle_installment = data_form.get('is-handle-installment')
        is_delete_table = data_form.get('is-delete-table')
        is_iir_vnd = data_form.get('is_iir_vnd')
        c = data_form.getlist('categories')
        ip = None 
        it = None 
        iir = None  
        lpi = None
        installment_type = None
        exchange_rate = data_form.get('exchange_rate')
        
        if is_handle_installment:
            ip = data_form.getlist('installment_payment')
            it = data_form.getlist('installment_term')
            lpi = data_form.get('late_payment_interest')
            iir = data_form.get('iir')
            installment_type = int(data_form.get('installment_type'))
        data = json.loads(data_json)

        try:
            with transaction.atomic():
                if is_delete_table:
                    models.SimStore.objects.all().update(d = True)

                unique_records = {}
                sim_store_instances = []

                for i in range(len(data)):
                    f = data[i][0]
                    id = f.replace('.', '')
                    pn = int(data[i][1].replace('.', '').replace(',', '')) * int(exchange_rate)
                    tt = detectPack(data[i][2])
                    t = getTelcoInput(data[i][3]) if data[i][3] else detectTelco(id)
                    t_detect = detectTelco(id)
                    note = data[i][4]
                    [cat, cat2] = get_cat_id(id, pn, is_handle_installment)
                    c2 = cat2
                    c = c if is_handle_cate and len(c) > 0 else cat

                    unique_records[id] = models.SimStore(
                        id = id,
                        f = f,
                        f0 = int(id[0]),
                        f1 = int(id[1]),
                        f2 = int(id[2]),
                        f3 = int(id[3]),
                        f4 = int(id[4]),
                        f5 = int(id[5]),
                        f6 = int(id[6]),
                        f7 = int(id[7]),
                        f8 = int(id[8]),
                        f9 = int(id[9]),
                        pn = pn,
                        pb = pn,
                        t = t if t else None,
                        t_detect = t_detect if t_detect else None,
                        c = c,
                        c2 = c2,
                        tt = tt,
                        ip = ip,
                        it = it,
                        iir = iir,
                        lpi = lpi,
                        installment_type = installment_type,
                        note = note,
                        h = False,
                        d = False
                    )

                sim_store_instances = list(unique_records.values())

                models.SimStore.objects.bulk_create(
                    sim_store_instances, 
                    batch_size=10000, 
                    update_conflicts=True, 
                    unique_fields=['id'], 
                    update_fields=['f','pn','pb','t','t_detect','d','c','c2','h','tt','ip','it','iir','installment_type','lpi','note','publish']
                    )
            messages.success(request, 'Dữ liệu đã được up thành công.')
        except Exception as e:
            messages.error(request, 'Dữ liệu up thất bại, vui lòng kiểm tra lại.')
            print("An error occurred:", str(e))
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        if request.method == 'POST' and 'post' in request.POST and 'yes' in request.POST['post']:
            if obj is not None:
                obj.d = True
                obj.save()
                messages.success(request, f"Đã xóa số  {obj.id} thành công !!!")
                return HttpResponseRedirect("/admin/sims/simstore")
        return super().delete_view(request, object_id, extra_context)

    def row_comments_action_view(self, request, pk):
        record = models.SimStore.objects.get(id=pk)
        if request.method == 'POST':
            form = SimStoreCommentsChangeForm(request.POST)
            if form.is_valid():
                # Get the new comment text
                new_comment = request.POST.get('new_comment')
                # Ensure that record.comment is a dictionary
                if not isinstance(record.comment, dict):
                    record.comment = {}
                # Add the new comment
                if new_comment:
                    index = str(len(record.comment))
                    new_comment_obj = {
                        'textComment': new_comment,
                        'commentedBy': request.user.username,
                        'commentedAt': timezone.now().strftime("%Y-%m-%d"),
                    }
                    record.comment[index] = new_comment_obj
                # Update the status for the record
                record.save()

                messages.success(request, f"Comments đã được thêm vào để giữ sim {record.id}.")
                return HttpResponse(status=200)
        else:
            form = SimStoreCommentsChangeForm()
            # Render the modal template
            context = dict(
                self.admin_site.each_context(request),
                object=record,
                opts=self.model._meta,
                title=_("Thêm comment"),
                data= record,
                form=form,
            )
            return TemplateResponse(request, 'admin/sims/simstore/comments_action_modal.html', context)
    
    def get_changelist(self, request, **kwargs):
        return CustomChangeList
    def delete_all(self, request):
        if request.method == 'POST':
            models.SimStore.objects.all().delete()
            messages.success(request, f"Đã xóa số  thành công !!!")
            return HttpResponseRedirect("/admin/sims/simstore")
        else:
            context = {
                **self.admin_site.each_context(request),
                "title": "Xác nhận xóa",
                'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
                }
            return TemplateResponse(request, "admin/sims/simstore/delete_all_sim_store.html", context)
# custom filter
class AccountReceivableInlineForm(forms.ModelForm):
    class Meta:
        model = models.AccountReceivable
        fields = ['comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].widget.attrs['rows'] = 1
        self.fields['comment'].widget.attrs['cols'] = 3
        self.fields['comment'].widget.attrs['style'] = 'width:100px'  # Set the number of columns
        self.fields['amount_payment'].widget.attrs['style'] = 'width:80px'
        self.fields['amount_remaining'].widget.attrs['style'] = 'width:80px'
        self.fields['user_create'].widget.attrs['style'] = 'width:80px'
        if 'amount_interest' in self.fields:
            self.fields['amount_interest'].widget.attrs['style'] = 'width:80px'
        if 'amount_interest_temp' in self.fields:
            self.fields['amount_interest_temp'].widget.attrs['style'] = 'width:80px'

class AccountReceivableInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            if form.instance.status == STATUS_AR_CHOICES.PAID:
                print("form.instance.status", form.instance.status)
                form.can_delete = False

# Define your inline formset using the custom form
AccountReceivableInlineFormSet = inlineformset_factory(models.SimOrder, models.AccountReceivable, form=AccountReceivableInlineForm, formset=AccountReceivableInlineFormSet, extra=0)

class AccountReceivableThoInline(admin.TabularInline):
    form=AccountReceivableInlineForm
    formset = AccountReceivableInlineFormSet
    fields = ('created_userpay','method_pay', 'user_create','amount_payment', 'amount_remaining', 'status', 'comment', 'attach_file', 'type')
    readonly_fields = ['code',]
    show_full_result_count=True
    model= models.AccountReceivable
    verbose_name = 'Công nợ thợ'
    verbose_name_plural="Công nợ thợ"
    extra=0

    # def formfield_for_dbfield(self, db_field, request, **kwargs):
    #     print("db_field", db_field)
    #     if db_field.name == 'type':
    #         kwargs['initial'] = TYPE_AR_CHOICES.THO  # Set default value for type field in MyInline1
    #     return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(type=TYPE_AR_CHOICES.THO)
        return queryset

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['user_create'].initial = request.user.username
        formset.form.base_fields['type'].initial = TYPE_AR_CHOICES.THO
        formset.form.base_fields['type'].widget = forms.HiddenInput(attrs={'style': 'display:none;'})
        formset.form.base_fields['amount_remaining'].widget.attrs['readonly'] = True

        return formset        
        
class AccountReceivableKHInline(admin.TabularInline):
    form=AccountReceivableInlineForm
    formset = AccountReceivableInlineFormSet
    fields = ('created_userpay','method_pay', 'user_create','amount_payment', 'amount_remaining', 'status', 'comment', 'attach_file', 'type')
    model = models.AccountReceivable
    verbose_name = 'công nợ KH'
    verbose_name_plural="công nợ KH"
    readonly_fields = ['code',]
    extra=0
    # def formfield_for_dbfield(self, db_field, request, **kwargs):
    #     print("kh11111111", db_field.name)
    #     if db_field.name == 'type':
    #         kwargs['initial'] = TYPE_AR_CHOICES.KH
    #     return super().formfield_for_dbfield(db_field, request, **kwargs)
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(type=TYPE_AR_CHOICES.KH)
        return queryset

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['user_create'].initial = request.user.username
        formset.form.base_fields['type'].initial = TYPE_AR_CHOICES.KH
        formset.form.base_fields['type'].widget = forms.HiddenInput(attrs={'style': 'display:none;'})
        formset.form.base_fields['amount_remaining'].widget.attrs['readonly'] = True
        return formset
class AccountReceivableKHTragopInline(admin.TabularInline):
    form=AccountReceivableInlineForm
    formset = AccountReceivableInlineFormSet
    fields = ('created_userpay', 'method_pay', 'user_create','amount_payment','amount_interest', 'amount_remaining', 'amount_interest_temp', 'status', 'comment', 'attach_file', 'type')
    model = models.AccountReceivable
    verbose_name = 'Công nợ KH'
    verbose_name_plural="Công nợ KH"
    readonly_fields = ['code']
    extra=0
    # def formfield_for_dbfield(self, db_field, request, **kwargs):
    #     print("formfield_for_dbfield", db_field.name)
    #     if db_field.name == 'type':
    #         kwargs['initial'] = TYPE_AR_CHOICES.KH  # Set default value for type field in MyInline1
    #     return super().formfield_for_dbfield(db_field, request, **kwargs)
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(type=TYPE_AR_CHOICES.KH)
        return queryset

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['user_create'].initial = request.user.username
        formset.form.base_fields['type'].initial = TYPE_AR_CHOICES.KH
        formset.form.base_fields['type'].widget = forms.HiddenInput(attrs={'style': 'display:none;'})
        formset.form.base_fields['amount_remaining'].widget.attrs['readonly'] = True
        formset.form.base_fields['amount_interest_temp'].widget.attrs['readonly'] = True

        return formset

@admin.register(models.AccountReceivable)
class AccountReceivableAdmin(admin.ModelAdmin):
    list_display = ('get_code', 'get_order_code', 'get_order_sim', 'get_order_sim_customer', 'get_order_store_type', 'formatted_amount_payment', 'formatted_amount_interest', 'formatted_amount_remaining', 'formatted_amount_interest_temp', 'status', 'created_at', 'created_userpay', 'get_method_pay_display', 'user_create', 'get_type_display')
    list_filter = ('status', 'method_pay', 'user_create', 'created_at', 'sim_order__store_type')
    search_fields = ('sim_order__sim', 'sim_order__phone', 'code', 'sim_order__code', 'sim_order__attributes__agency_id')
    readonly_fields = ('get_order_sim', 'get_order_sim_customer', 'get_order_store_type')

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "Công nợ"
        self.opts.verbose_name = "Công nợ"

    def get_method_pay_display(self, obj):
        if obj.method_pay == PAY_METHOD_CHOICES.CASH:
            return format_html('<span>Tiền mặt</span>')
        else:
            return format_html('<span>Chuyển khoản</span>')

    get_method_pay_display.short_description = models.AccountReceivable._meta.get_field('method_pay').verbose_name

    def get_order_code(self, obj):
        if obj.sim_order:
            return obj.sim_order.code
        else:
            return ''
    
    def get_order_sim(self, obj):
        if obj.sim_order:
            return obj.sim_order.sim
        else:
            return ''
    get_order_sim.short_description = "Số đặt mua"

    def get_order_sim_customer(self, obj):
        if obj.sim_order:
            return obj.sim_order.phone
        else:
            return ''
    get_order_sim_customer.short_description = "Số khách hàng"

    def get_order_store_type(self, obj):
        store_type = dict(STORE_TYPES.choices).get(obj.sim_order.store_type, '')
        agency_id_id = obj.sim_order.attributes.get('agency_id', '')
        if agency_id_id:
            return format_html('<div class="detail-name">{}</div><div style="color: var(--link-fg);"> Mã kho: {}</div>', store_type, agency_id_id)
        else:
            return format_html('<div class="detail-name">{}</div>', store_type)
    get_order_store_type.short_description = "Nguồn kho"

    def get_order_amount_interest_temp(self, obj):
        if obj.sim_order:
            return obj.sim_order.amount_interest_temp
        else:
            return ''
    get_order_amount_interest_temp.short_description = "Lãi tạm tính"
    
    def get_order_amount(self, obj):
        if obj.order:
            return obj.sim_order.amount_payment
        else:
            return ''
    change_form_template = 'admin/sims/simstore/components/customize_warning.html'
    
    def get_type_display(self, obj):
        return obj.get_type_display()
    get_type_display.short_description = "Loại công nợ"

    
    def formatted_amount_payment(self, obj):
        return formatCurrency(obj.amount_payment)
    formatted_amount_payment.short_description = "Tiền thanh toán"

    def formatted_amount_interest(self, obj):
        return formatCurrency(obj.amount_interest)
    formatted_amount_interest.short_description = "Tiền lãi"


    def formatted_amount_remaining(self, obj):
        return formatCurrency(obj.amount_remaining)
    formatted_amount_remaining.short_description = "Gốc còn lại"

    def formatted_amount_interest_temp(self, obj):
        return formatCurrency(obj.amount_interest_temp)
    formatted_amount_interest_temp.short_description = "Lãi tạm tính"

    def get_code(self, obj):
        return obj.code
    get_code.short_description = "Mã công nợ"

    get_order_code.short_description = "Mã đơn hàng"
    get_order_amount.short_description="Giá SIM"

@admin.register(models.SimOrder)
class SimOrderAdmin(admin.ModelAdmin):
    form = SimOrderAdminForm
    list_display = ('row_code_created_at', 'row_sim_amount', 'row_agency_id', 'row_name', 'sale_pic', 'row_status_action_popup', 'sale_notes_display')
    exclude = ['createdAt', 'updatedAt',]
    list_filter = [CustomCreatedAtFilter, 'status', 'order_type', CustomPushedFilter, 'sale_pic', 'pay_kh_status', 'pay_tho_status']
    search_fields = ["code", "name", "phone","sim", "phone", "attributes__agency_id"]
    readonly_fields = ['code', 'get_created_at', 'sale_notes_readonly', 'pushed', 'get_amount_format',  'get_store_type', 'telco_id', 'c2','get_price_collection', 'get_worker_code']
    actions = [pushwebhook_order_action, assign_order_to_pic_action]
    inlines = [AccountReceivableKHInline, AccountReceivableKHTragopInline, AccountReceivableThoInline]

    def get_fieldsets(self, request, obj=None):
        if obj and obj.order_type != REQUEST_CHOICES.INSTALLMENT:
            if obj.order_type == REQUEST_CHOICES.REQUEST:
                return (
                        (_('Đơn hàng'), {
                            'fields': ('code', 'get_created_at', 'order_type', 'id_order_type', 'source_text', 'status', 'pushed', 'reason_text', 'other_option', 'sale_notes')
                        }),
                        (_('Chi tiết yêu cầu'), {
                            'fields': ('sale_pic', 'sim', 'telco_id', 'c2', 'amount', 'pg', 'store_type', 'id_store_type', 'transport', 'costs', 'note_costs', 'name_deliver', 'phone_deliver', 'pay_kh_status', 'pay_tho_status')
                        }),
                        (_('Khách hàng'), {
                            'fields': ('name', 'phone', 'address')
                        }),
                    )
            if obj.store_type == STORE_TYPES.KHO_SIM:
                return (
                        (_('Đơn hàng'), {
                            'fields': ('code', 'get_created_at', 'order_type', 'id_order_type', 'source_text', 'status', 'pushed', 'reason_text', 'other_option', 'sale_notes')
                        }),
                        (_('Chi tiết yêu cầu'), {
                            'fields': ('sale_pic', 'sim', 'telco_id', 'c2', 'amount', 'pg', 'get_store_type', 'id_store_type', 'transport', 'costs', 'note_costs', 'name_deliver', 'phone_deliver', 'pay_kh_status', 'pay_tho_status')
                        }),
                        (_('Khách hàng'), {
                            'fields': ('name', 'phone', 'address')
                        }),
                    )
            else:
                return (
                        (_('Đơn hàng'), {
                            'fields': ('code', 'get_created_at', 'order_type', 'id_order_type', 'source_text', 'status', 'pushed', 'reason_text', 'other_option', 'sale_notes', 'get_price_collection', 'get_worker_code')
                        }),
                        (_('Chi tiết yêu cầu'), {
                            'fields': ('sale_pic', 'sim', 'telco_id', 'c2', 'amount', 'pg', 'get_store_type', 'id_store_type', 'transport', 'costs', 'note_costs', 'name_deliver', 'phone_deliver', 'pay_kh_status', 'pay_tho_status')
                        }),
                        (_('Khách hàng'), {
                            'fields': ('name', 'phone', 'address')
                        }),
                    )
        elif obj and obj.order_type == REQUEST_CHOICES.INSTALLMENT:
            if obj.store_type == STORE_TYPES.KHO_SIM:
                return (
                        (_('Đơn hàng'), {
                            'fields': ('code', 'get_created_at', 'order_type','id_order_type', 'source_text', 'status', 'pushed', 'reason_text', 'other_option', 'sale_notes')
                        }),
                        (_('Chi tiết yêu cầu'), {
                            'fields': ('sale_pic', 'sim', 'telco_id', 'c2', 'amount', 'pg','percentUpfront', 'monthNumber', 'installment_type', 'iir', 'get_store_type','id_store_type', 'transport', 'costs', 'note_costs', 'name_deliver', 'phone_deliver', 'pay_kh_status', 'pay_tho_status')
                        }),
                        (_('Khách hàng'), {
                            'fields': ('name', 'phone', 'address')
                        }),
                    )
            else:
                return (
                        (_('Đơn hàng'), {
                            'fields': ('code', 'get_created_at', 'order_type','id_order_type', 'source_text', 'status', 'pushed', 'reason_text', 'other_option', 'sale_notes',  'get_price_collection', 'get_worker_code')
                        }),
                        (_('Chi tiết yêu cầu'), {
                            'fields': ('sale_pic', 'sim', 'telco_id', 'c2', 'amount', 'pg','percentUpfront', 'monthNumber', 'installment_type', 'iir', 'get_store_type','id_store_type', 'transport', 'costs', 'note_costs', 'name_deliver', 'phone_deliver', 'pay_kh_status', 'pay_tho_status')
                        }),
                        (_('Khách hàng'), {
                            'fields': ('name', 'phone', 'address')
                        }),
                    )
        return (
                (_('Đơn hàng'), {
                    'fields': ('code', 'get_created_at', 'order_type','id_order_type', 'source_text', 'status', 'reason_text', 'other_option', 'sale_notes')
                }),
                (_('Chi tiết yêu cầu'), {
                    'fields': ('sale_pic', 'sim', 'telco_id', 'c2', 'pg', 'amount', 'store_type', 'transport', 'costs', 'note_costs', 'name_deliver', 'phone_deliver')
                }),
                (_('Khách hàng'), {
                    'fields': ('name', 'phone', 'address')
                }),
            )
    def has_change_permission(self, request, obj=None):
        if obj is None:
            # No object is being edited (create page)
            return False
        else:
            # Allow editing existing objects
            return super().has_change_permission(request, obj)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'sale_pic':
            # Set the default selected option to the currently logged-in user
            kwargs['initial'] = request.user.id
            kwargs['queryset'] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        # Replace "status" with the name of your field
        order_type = obj.order_type if obj else None
        store_type = obj.store_type if obj else None
        if order_type == REQUEST_CHOICES.COMMON:
            if store_type == STORE_TYPES.KHO_SIM:
                inlines_to_show = [AccountReceivableKHInline]
            else:
                inlines_to_show = [AccountReceivableKHInline, AccountReceivableThoInline]
        elif order_type == REQUEST_CHOICES.INSTALLMENT:
            if store_type == STORE_TYPES.KHO_SIM:
                inlines_to_show = [AccountReceivableKHTragopInline]
            else:
                inlines_to_show = [AccountReceivableKHTragopInline, AccountReceivableThoInline]
        else:
            # Default: Show all inlines
            inlines_to_show = []
        # Filter the inline_instances based on inlines_to_show
        filtered_inline_instances = [
            inline for inline in inline_instances if type(inline) in inlines_to_show
        ]
        return filtered_inline_instances
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "Đơn hàng"
        self.opts.verbose_name = "Đơn hàng"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # only show the `reason_text` field if `status` is `Hủy`
        if obj and obj.status == STATUS_CHOICES.CANCELED:
            form.base_fields['reason_text'].widget = forms.TextInput()
        else:
            form.base_fields['reason_text'].widget = forms.HiddenInput()
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            uneditable_fields = ['order_type', 'source_text',]
            if obj.order_type != REQUEST_CHOICES.REQUEST:
                uneditable_fields.append('sim')
            return readonly_fields + uneditable_fields
        else:
            return readonly_fields

    def change_view(self, request, object_id, form_url='', extra_context=None):
        log_entries = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(self.model).id,
                                              object_id=object_id)
        extra_context = extra_context or {}
        extra_context['log_entries'] = log_entries
        sim_store = models.SimOrder.objects.get(id=object_id)
        if sim_store and sim_store.store_type == STORE_TYPES.KHO_APPSIM:
            extra_context['data_kho'] = self.list_check_kho(request=request, sim = sim_store.sim)
        else:
            extra_context['data_kho'] = None
        return super().change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('change-status-action/<int:pk>', self.admin_site.admin_view(self.row_status_action_view),
                 name='sim_status_change_action'),
            path('change-sale_notes-action/<int:pk>', self.admin_site.admin_view(self.row_sale_notes_action_view),
                 name='sim_sale_notes_change_action'),
            path('get-detail-sim-store/<str:sim>', self.admin_site.admin_view(self.getSimDetailApi), name='get-sim-detail-api'),
        ]
        return custom_urls + urls
        
    def row_status_action_popup(self, obj):
        url = reverse('admin:sim_status_change_action', kwargs={'pk': obj.id})
        status_text = obj.get_status_display()
        status_kh = dict(STATUS_PAY_CHOICES.choices).get(obj.pay_kh_status, 'Chưa thanh toán')
        status_tho = dict(STATUS_PAY_CHOICES.choices).get(obj.pay_tho_status, 'Chưa thanh toán')
        return format_html(
            '<div>TT Đơn hàng: <a href="javascript:void(0);" onclick="showPopupModal(\'{}\');" class="custom-action-popup">{}</a></div><div>TT Thanh toán KH: {}</div><div>TT Thanh toán Thợ: {}</div>', url, status_text, status_kh, status_tho)
    row_status_action_popup.short_description = 'Trạng thái'

    def row_code_created_at(self, obj):
        return format_html('%s<br /> <span style="font-weight:400">%s</span>' % (
            obj.code, vn_date_format(obj.createdAt)))
    row_code_created_at.short_description = 'Mã ĐH/ Ngày tạo'

    def row_sim_amount(self, obj):
        amount = formatCurrency(obj.amount) if obj.amount else ''
        amount = obj.amount
        if amount:
            return format_html('<div class="detail-sim">{}</div><div style="color: var(--link-fg);">Giá: {}</div><div>{}</div>',
                obj.sim, formatCurrency(amount), get_label_from_value(REQUEST_CHOICES.choices, obj.order_type))
        else:
            return format_html('<div class="detail-sim">{}</div><div>{}</div>',
                obj.sim, get_label_from_value(REQUEST_CHOICES.choices, obj.order_type))
    row_sim_amount.short_description = 'Sim / Giá trị'

    def row_name(self, obj):
        address = obj.address if obj.address else ''
        if address:
            return format_html('<div class="detail-name">Họ và tên: {}</div><div style="color: var(--link-fg);"> Số liên hệ: {}</div><div class="detail-address">Địa chỉ: {}</div>', obj.name, obj.phone, address)
        else:
            return format_html('<div class="detail-name">Họ và tên: {}</div><div style="color: var(--link-fg);"> Số liên hệ: {}</div>', obj.name, obj.phone)        
    row_name.short_description = 'khách hàng'

    def sale_notes_display(self, obj):
        url = reverse('admin:sim_sale_notes_change_action', kwargs={'pk': obj.id})
        truncated_notes = '📝'
        notes_html = ""
        if obj.sale_notes and isinstance(obj.sale_notes, dict):
            for index, note in obj.sale_notes.items():
                expected_keys = ['notedBy', 'textNote', 'notedAt']
                # Check if all expected keys are present in the note
                if all(key in note for key in expected_keys):
                    username = note['notedBy']
                    text_note = note['textNote']
                    notedAt = note['notedAt']
                    # Escape HTML to prevent XSS attacks
                    escaped_text_note = escape(text_note)
                    # Display each note in the tooltip
                    notes_html += f'<b>{notedAt} - {username}:</b> {escaped_text_note}<br/>'
                else:
                    notes_html = ''
        # Truncate the notes to <= 20 chars
        truncated_notes = format_html('<a href="javascript:void(0);" onclick="showPopupModal(\'{}\');" class="editable-field" data-pk="{}" data-field="sale_notes" title="{}">{}</a><br/>',
                    url,
                    truncated_notes,
                    truncated_notes,
                    truncated_notes,
                )
                
        truncated_notes = notes_html  + truncated_notes
        return format_html(truncated_notes)
        return None
    sale_notes_display.short_description = 'Ghi chú'

    def sale_notes_readonly(self, obj):
        notes_html = ""
        if obj.sale_notes:
            for index, note in obj.sale_notes.items():
                username = note.get('notedBy', '')
                text_note = note.get('textNote', '')
                noted_at = note.get('notedAt', '')
                # Format the display for each note
                note_display = f"{username} ({noted_at}): {text_note}"
                # Escape HTML to prevent XSS attacks
                escaped_note_display = escape(note_display)
                notes_html += f"{escaped_note_display}<br>"
        return format_html(notes_html)
    sale_notes_readonly.short_description = 'Ghi chú'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']  # Remove the default delete_selected action
        return actions

    def row_status_action_view(self, request, pk):
        if request.method == 'POST':
            form = SimOrderStatusChangeForm(request.POST)
            if form.is_valid():
                status = form.cleaned_data['status']
                record = models.SimOrder.objects.get(id=pk)
                
                old_status = record.get_status_display()
                record.status = status
                new_status = dict(STATUS_CHOICES.choices).get(int(status), '')
                # Log the changes of the `status`
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(record).pk,
                    object_id=record.id,
                    object_repr=str(record),
                    action_flag=CHANGE,
                    change_message=f'Đã thay đổi trạng thái từ "{old_status}" thành "{new_status}".'
                )

                if record.status == str(STATUS_CHOICES.COMPLETED) or record.status == str(STATUS_CHOICES.DELIVERING) or record.status == str(STATUS_CHOICES.DELIVERED):
                    try:
                        sim = models.SimStore.objects.get(id=record.sim)
                        # Set sim `d` field to `True` if order has completed
                        sim.d = True
                        sim.save()
                    except ObjectDoesNotExist:
                        pass
                record.save()
                messages.success(request, f"Trạng thái của đơn hàng {record.code} với sim {record.sim} đã được cập nhật.")
                return HttpResponse(status=200)
        else:
            record = models.SimOrder.objects.get(id=pk)
            form = SimOrderStatusChangeForm(status_initial_selection=record.status)
            # Render the modal template
            context = dict(
                self.admin_site.each_context(request),
                object=record,
                opts=self.model._meta,
                title=_("Chuyển đổi trạng thái"),
                data= record,
                form=form,
            )
            return TemplateResponse(request, 'admin/sims/simorder/status_action_modal.html', context)

    def row_sale_notes_action_view(self, request, pk):
        record = models.SimOrder.objects.get(id=pk)
        if request.method == 'POST':
            form = SimOrderSaleNotesChangeForm(request.POST)
            if form.is_valid():
                # Get the new note text
                new_note = request.POST.get('new_note')
                # Ensure that record.note is a dictionary
                if not isinstance(record.sale_notes, dict):
                    record.sale_notes = {}
                # Add the new note as a new object to sale_notes
                if new_note:
                    index = str(len(record.sale_notes))
                    new_note_obj = {
                        'textNote': new_note,
                        'notedBy': request.user.username,
                        'notedAt': timezone.now().strftime("%Y-%m-%d"),
                    }
                    record.sale_notes[index] = new_note_obj
                    # Log the changes of the `sale_notes`
                    LogEntry.objects.log_action(
                        user_id=request.user.id,
                        content_type_id=ContentType.objects.get_for_model(record).pk,
                        object_id=record.id,
                        object_repr=str(record),
                        action_flag=CHANGE,
                        change_message=f'Đã thêm ghi chú "{new_note_obj["textNote"]}".'
                    )
                record.save()

                messages.success(request, f"Ghi chú của đơn hàng {record.code} với sim {record.sim} đã được cập nhật.")
                return HttpResponse(status=200)
        else:
            form = SimOrderSaleNotesChangeForm()
            # Render the modal template
            context = dict(
                self.admin_site.each_context(request),
                object=record,
                opts=self.model._meta,
                title=_("Thêm ghi chú"),
                data= record,
                form=form,
            )
            return TemplateResponse(request, 'admin/sims/simorder/sale_notes_action_modal.html', context)

    def get_created_at(self, obj):
        if obj.createdAt:
            return vn_date_format(obj.createdAt)
        else:
            return ''
    get_created_at.short_description = 'Tạo lúc'

    def get_store_type(self, obj):
        if obj.store_type:
            return dict(STORE_TYPES.choices)[obj.store_type]
        else:
            return ''
    get_store_type.short_description = 'Kho'

    def row_agency_id(self, obj):
        store_type = dict(STORE_TYPES.choices).get(obj.store_type, '')
        agency_id = obj.attributes.get('agency_id', '')
        if agency_id:
            return format_html('<div class="detail-name">{}</div><div style="color: var(--link-fg);"> Mã kho: {}</div>', store_type, ','.join(str(x) for x in agency_id))
        else:
            return format_html('<div class="detail-name">{}</div>', store_type)
    row_agency_id.short_description = 'Kho'
    
    def get_amount_format(self, obj):
        if obj.amount:
            return formatCurrency(obj.amount)
        else:
            return ''
    get_amount_format.short_description = 'Giá bán'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if qs is not None:
            if not request.user.is_superuser:
                # Show orders associated with the user in sale_pic
                return qs.filter(sale_pic=request.user)
            else:
                # Show all orders for superuser
                return qs

    def sale_pic_name(self, obj):
        if obj.sale_pic:
            url = reverse('admin:auth_user_change', args=[obj.sale_pic.id])
            return format_html('<a href="{}">{}</a>', url, obj.sale_pic.get_username())
        return None
    sale_pic_name.short_description = 'Phụ trách'

    def get_price_collection(self, obj):
        if obj.attributes:
            pg = obj.attributes.get('pg', '')
            return format_html('<span class="price-collection">{}</span>', formatCurrency(pg))
        return ''
    get_price_collection.short_description = 'Giá thu'

    def get_worker_code(self, obj):
        if obj.attributes:
            agency_id = obj.attributes.get('agency_id', '')
            return format_html('<span class="worker-code">{}</span>', ','.join(str(x) for x in agency_id))
        return ''
    get_worker_code.short_description = 'Mã kho'

    def getSimDetailApi(self, request, sim): 
        if sim:
            tenant = request.tenant
            simDetail = getSimDetail(sim, tenant)
            list_kho = self.list_check_kho(request=request, sim = sim)
            template = loader.get_template('admin/sims/simorder/tbl_kho_sim.html')
            template_kho = template.render(list_kho) if list_kho.get('agencies', '') else ''
            if simDetail:
                if '_state' in simDetail:
                    simDetail.pop('_state', None)
                return JsonResponse({"template_kho": template_kho, "simDetail": simDetail})
            else:
                return JsonResponse({'error': f'Không tìm thấy sim {sim}'}, status=404)
        else:
            return JsonResponse({'error': 'Số sim không hợp lệ'}, status=400) 

    def list_check_kho(self, request, sim):
        tenant = request.tenant
        paramsObj= {'store_type': STORE_TYPES.KHO_MIX, 'p': 1, 'q': sim}
        data_form = request.GET
        path = f"/{data_form['path']}/" if data_form.get('path', None) else '/'
        filterObj = getSimUrlFilter(path, paramsObj)
        data = getSims(filterObj, tenant, request, '/search/query3-not-mix')
        search_store_list = data['data']

        agencies = {}
        agency_ids = []
        phonesInfo = []
        if search_store_list is not None:
            for item in search_store_list:
                if 'highlight' in item and item['highlight']:
                    agency_ids.extend(map(str, item['s3']))

        sellers = getSellerInfo(agency_ids)
        if sellers:
            for seller in sellers:
                seller_id = seller['agency_id']
                agencies[int(seller_id)] = seller
        if sim:
            try:
                phonesInfo = getPhoneInfo(sim, tenant)
            except (ValueError, TypeError):
                return []
            context = dict(
                phonesInfo = phonesInfo,
                search_store_list = search_store_list,
                agencies = agencies,
            )
            return context
    
    def save_model(self, request, obj, form, change):
        if obj.attributes is None:
            obj.attributes = {}
        if form.cleaned_data.get('installment_type', 1):
            obj.attributes['installment_type'] = int(form.cleaned_data.get('installment_type', 1))
        if form.cleaned_data.get('id_store_type', 1):
            obj.store_type = int(form.cleaned_data.get('id_store_type', 1))
        if obj.store_type == STORE_TYPES.KHO_APPSIM and request.POST.get('agency_id', ''):
            obj.attributes['agency_id'] = [int(request.POST.get('agency_id', ''))] 
        if form.cleaned_data.get('iir', None):  
            obj.attributes['iir'] = form.cleaned_data.get('iir', None)  
        if form.cleaned_data.get('percentUpfront', None): 
            obj.attributes['percentUpfront'] = form.cleaned_data.get('percentUpfront', None)  
        if form.cleaned_data.get('monthNumber', None): 
            obj.attributes['monthNumber'] = form.cleaned_data.get('monthNumber', None) 
        super().save_model(request, obj, form, change)
        
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Perform additional logic to update the order here
        order = form.instance
        update_payment_status(order)
        order.save()

#custom User add more extra field
class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete=False
class AccountUserAdmin(AuthUserAdmin):
    def add_view(self, request, extra_context=None):
        self.inlines = []
        return super().add_view(request, extra_context=extra_context)

    def change_view(self, *args, **kwargs) -> HttpResponse:
        self.inlines = [UserProfileInline]
        return super(AccountUserAdmin, self).change_view(*args, **kwargs)

# dang ky page config seo and custom sim query page    
@admin.register(ArticlePage)
class ArticlePageSimConfigAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'slug' in form.base_fields:
            form.base_fields['slug'].widget = CustomHTMLSlug(form)
        return form
    
    list_display = ('title', 'status', 'slug', 'user', 'publishedAt')
    list_filter = ('user', 'status', 'category', 'publishedAt')
    search_fields = ["title", "excerpt"]
    exclude = ["type"]
    form = ArticlePageSimConfigAdminForm
    fieldsets = (
        (_('Thông tin chung'), {
           'fields': ('title', 'slug', 'tags', 'featured', 'excerpt', 'featured_image', 'body', 'publishedAt','category', 'status')
        }),
        (_('Seo Meta'), {
            'classes': ('collapse', 'open'),
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'meta_canonical','related_pages', 'headscript'),
        }),
        (_('Cấu hình Sim'), {
            'classes': ('collapse', 'open'),
            'fields': ('priority_numbers','priority_stores','gte','lte','d','t', 'store_type', 'query_mandatory'),
        }),
    )
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.opts.verbose_name_plural = "Cài đặt seo page sim"
        self.opts.app_label = "seo_optimizer"
    change_form_template = 'admin/sims/simstore/components/customize_warning.html'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            Q(type=Article.Type.PAGE)
        )
    # prepopulated_fields = {'slug': ('title',), }

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        autoClearCache(request)
        super().save_model(request, obj, form, change)

admin.site.unregister(User)
admin.site.register(User, AccountUserAdmin)    