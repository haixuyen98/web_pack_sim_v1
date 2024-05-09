from django import forms
from . import models
import json
from django import forms
from blog.models import ArticlePage
import json
import re
from sims.common.choices import NHA_MANG_CHOICES, SORTING_CHOICES, STORE_TYPES, INSTALLMENT_TYPE_CHOICES, get_label_from_value
from core.settings import EMPTY_CHOICE
from sims.common.choices import (
    STATUS_CHOICES,
    STATUS_PAY_CHOICES,
)
from sims.services.sim_service import getSimDetail
from core.helpers import formatCurrency, get_current_tenant
from django.core.exceptions import ObjectDoesNotExist


class SimStoreCommentsChangeForm(forms.Form):
    new_comment = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Add new comment...'}), required=False)
    def __init__(self, *args, **kwargs):
        super(SimStoreCommentsChangeForm, self).__init__(*args, **kwargs)

class CommentsField(forms.CharField):
    def clean(self, value):
        # Override the clean method to handle input
        return super().clean(value)

class SimStoreAdminForm(forms.ModelForm):
    # Use the custom form field for the note field
    comments = CommentsField(widget=forms.Textarea, required=False)

    class Meta:
        model = models.SimStore
        fields = '__all__'

class SimOrderStatusChangeForm(forms.Form):
    status = forms.ChoiceField(choices=STATUS_CHOICES.choices)
    def __init__(self, *args, **kwargs):
        status_initial_selection = kwargs.pop('status_initial_selection', None)
        super(SimOrderStatusChangeForm, self).__init__(*args, **kwargs)
        self.fields['status'].initial = status_initial_selection
        
class SimOrderSaleNotesChangeForm(forms.Form):
    new_note = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Add new note...'}), required=False)
    def __init__(self, *args, **kwargs):
        super(SimOrderSaleNotesChangeForm, self).__init__(*args, **kwargs)

class SaleNotesField(forms.CharField):
    def clean(self, value):
        # Override the clean method to handle input
        return super().clean(value)

class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return value or ''


class SimOrderAdminForm(forms.ModelForm):
    # Use the custom form field for the sale_notes field
    sale_notes = SaleNotesField(widget=forms.Textarea, required=False)
    sale_notes = forms.CharField(widget=forms.HiddenInput(), required=False)
    # installment_type = forms.CharField(
    #     widget=ReadOnlyWidget(),
    #     label='Kiểu trả góp' )
    percentUpfront = forms.CharField(
        required=False,
        label='Dự tính trả trước')
    monthNumber = forms.CharField(
        required=False,
        label='Số tháng trả lãi')
    
    iir = forms.CharField(
        required=False,
        label='Lãi suất')
    # lpi = forms.CharField(
    #     widget=ReadOnlyWidget(),
    #     label='Lãi suất trâ chậm')
    installment_type = forms.ChoiceField(label='Chọn đơn vị lãi suất', choices=INSTALLMENT_TYPE_CHOICES.choices,widget=forms.RadioSelect, required=False)
    pg = forms.CharField(widget = forms.HiddenInput(), required = False, label='Giá thu')
    id_store_type = forms.CharField(widget = forms.HiddenInput(), required = False, label='Kho')
    id_order_type = forms.CharField(widget = forms.HiddenInput(), required = False, label='Loại đơn')

    class Meta:
        model = models.SimOrder
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        tenant = get_current_tenant()
        sim = self.cleaned_data.get('sim')
        result = getSimDetail(sim, tenant)

        if sim:
            if not result:
                raise forms.ValidationError(f'Sim không hợp lệ hoặc không tồn tại sim số {sim} trong kho.')
            else:
                cleaned_data['telco_id'] = result.get('t')
                cleaned_data['c2'] = result.get('c2')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance'] is not None:
            attributes = kwargs['instance'].attributes
            store_type = kwargs['instance'].store_type
            order_type = kwargs['instance'].order_type
            installment_type_val = attributes.get('installment_type', None)
            if installment_type_val:
                self.fields['installment_type'].initial = f"{attributes.get('installment_type', None)}" 
                installment_type_val = get_label_from_value(INSTALLMENT_TYPE_CHOICES.choices, installment_type_val)
            # self.fields['installment_type'].initial = installment_type_val
            if attributes.get('iir', None):
                self.fields['iir'].initial = f"{attributes.get('iir', None)}" 
                self.fields['iir'].help_text = f"<span class='txt_iir'>{installment_type_val}</span>"
            # self.fields['lpi'].initial = f"{attributes.get('lpi', None)} {installment_type_label}"
            
            percent_first = attributes.get('percentUpfront', None)
            if percent_first:
                self.fields['percentUpfront'].initial = f"{attributes.get('percentUpfront', '')}"
            if 'monthNumber' in attributes:
                self.fields['monthNumber'].initial = f"{attributes.get('monthNumber', '')}"
            if 'pg' in attributes:
                self.fields['pg'].initial = f"{attributes.get('pg', '')}"
            if store_type:
                self.fields['id_store_type'].initial = f"{store_type}"
            if order_type:
                self.fields['id_order_type'].initial = f"{order_type}"

    def save(self, commit=True):
        # Override the save method to handle the read-only `telco_id` and `c2` fields
        instance = super().save(commit=False)
        if self.cleaned_data.get('sim') is not None:
            instance.telco_id = self.cleaned_data['telco_id']
            instance.c2 = self.cleaned_data['c2']
        if instance.sim is not None:
            status = self.cleaned_data.get('status')
            pay_kh_status = self.cleaned_data.get('pay_kh_status')
            if status is not None or pay_kh_status is not None:
                status_choices = [STATUS_CHOICES.COMPLETED, STATUS_CHOICES.DELIVERING, STATUS_CHOICES.DELIVERED]
                pay_kh_status_choices = [STATUS_PAY_CHOICES.PAIDING, STATUS_PAY_CHOICES.PAID]
                if status in status_choices or pay_kh_status in pay_kh_status_choices:
                    try:
                        sim = models.SimStore.objects.get(id=instance.sim)
                        # Set sim `d` field to `True` if order has completed
                        sim.d = True
                        sim.save()
                    except ObjectDoesNotExist:
                        pass
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    # Add more fields as needed
class SimStoreCsvImportForm(forms.Form):
    csv_upload = forms.FileField()

class ArticlePageSimConfigAdminForm(forms.ModelForm):
    # store_config = SimQueryJSONFormField(required=False)
    NHA_MANG_CHOICES_1 = EMPTY_CHOICE +NHA_MANG_CHOICES
    
    store_type_data = EMPTY_CHOICE + tuple(STORE_TYPES.choices)
    
    priority_numbers = forms.CharField(widget=forms.Textarea, required=False, label="Số ưu tiên", help_text="(Có thể nhập nhiều ID, mỗi ID cách nhau bởi một lần xuống dòng)")
    priority_stores = forms.CharField(widget=forms.Textarea, required=False, label="Kho ưu tiên", help_text="(Có thể nhập nhiều ID, mỗi ID cách nhau bởi một lần xuống dòng)")
    gte = forms.IntegerField(required=False,label= "Ưu tiên Giá lớn hơn")
    lte = forms.IntegerField(required=False, label="Ưu tiên Giá nhỏ hơn")
    d = forms.ChoiceField(label="Mặc định sắp xếp",choices=SORTING_CHOICES,widget=forms.Select, required=False)
    t = forms.ChoiceField(label="Ưu tiên Nhà mạng", choices=NHA_MANG_CHOICES_1,widget=forms.Select, required=False)
    query_mandatory = forms.CharField(label="Điều kiện query bắt buộc", required=False,widget=forms.TextInput(attrs={'style': 'width: 400px;'}))
    store_type = forms.ChoiceField(label="Kho Sim", choices=store_type_data,widget=forms.Select, required=False, help_text="Chỉ query trên kho này")
    class Meta:
        model = ArticlePage
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.store_config:
            store_config_data = self.instance.store_config
            self.fields['priority_numbers'].initial = store_config_data.get('priority_numbers')
            self.fields['priority_stores'].initial = store_config_data.get('priority_stores')
            self.fields['gte'].initial = store_config_data.get('gte')
            self.fields['lte'].initial = store_config_data.get('lte')
            self.fields['d'].initial = store_config_data.get('d')
            self.fields['t'].initial = store_config_data.get('t')
            self.fields['store_type'].initial = store_config_data.get('store_type')
            self.fields['query_mandatory'].initial = store_config_data.get('query_mandatory')

    def clean(self):
        cleaned_data = super().clean()
        store_config_data = cleaned_data.get('store_config')
        if store_config_data:
            try:
                parsed_data = json.loads(store_config_data)
                cleaned_data['priority_numbers'] = parsed_data.get('priority_numbers')
                cleaned_data['priority_stores'] = parsed_data.get('priority_stores')
                cleaned_data['gte'] = parsed_data.get('gte')
                cleaned_data['lte'] = parsed_data.get('lte')
                cleaned_data['d'] = parsed_data.get('d')
                cleaned_data['t'] = parsed_data.get('t')
                cleaned_data['store_type'] = parsed_data.get('store_type')
                cleaned_data['query_mandatory'] = parsed_data.get('query_mandatory')
            except json.JSONDecodeError:
                raise forms.ValidationError('Invalid JSON data')
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)

        store_config_data = {
            'priority_numbers': self.cleaned_data.get('priority_numbers', None),
            'priority_stores': self.cleaned_data.get('priority_stores', None),
            'gte': self.cleaned_data.get('gte', None),
            'lte': self.cleaned_data.get('lte', None),
            'd': self.cleaned_data.get('d', None),
            't': self.cleaned_data.get('t', None),
            'store_type': self.cleaned_data.get('store_type', None),
            'query_mandatory': self.cleaned_data.get('query_mandatory', None)
        }
        instance.store_config = store_config_data
        instance.save()
        return instance

class FengShuiForm(forms.Form):
    birthday = forms.DateField(
        label='Ngày sinh', 
        widget=forms.TextInput(
            attrs={
                'class': 'datetime__column--input', 
                'type': 'date'
            }
        ),
        initial='1995-01-01'
    )
    appt = forms.TimeField(
        label='Giờ sinh', 
        widget=forms.TextInput(
            attrs={
                'class': 'datetime__column--input', 
                'type': 'time', 
                'min': '00:00',  
                'max': '23:59'
            }
        ),
        initial='00:00',
        input_formats=['%H:%M']
    )
    sex = forms.ChoiceField(
        label='Giới tính', 
        choices=[('men', 'Nam'), ('women', 'Nữ')], 
        widget=forms.RadioSelect(
            attrs={'class': 'gioiTinh__radio'}
        ),
        initial='men'
    )

class FengShuiFortuneForm(forms.Form):
    birthday = forms.DateField(
        label='Ngày sinh', 
        widget=forms.TextInput(
            attrs={
                'class': 'datetime__column--input', 
                'type': 'date'
            }
        ),
        initial='1995-01-01'
    )
    appt = forms.TimeField(
        label='Giờ sinh', 
        widget=forms.TextInput(
            attrs={
                'class': 'datetime__column--input', 
                'type': 'time', 
                'min': '00:00',  
                'max': '23:59'
            }
        ),
        initial='00:00',
        input_formats=['%H:%M']
    )
    sex = forms.ChoiceField(
        label='Giới tính', 
        choices=[('men', 'Nam'), ('women', 'Nữ')], 
        widget=forms.RadioSelect(
            attrs={'class': 'gioiTinh__radio'}
        ),
        initial='men'
    )
    phone = forms.CharField(
        label='Số điện thoại',
        widget=forms.TextInput(
            attrs={
                'class': 'phone__column--input',
                'type': 'tel',
                'placeholder': 'Nhập số điện thoại'
            }
        ),
        max_length=11,
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit():
            raise forms.ValidationError("(*) Số điện thoại chỉ được chứa các chữ số.")
        if not phone.startswith('0'):
            raise forms.ValidationError("(*) Số điện thoại phải bắt đầu bằng số 0.")
        if len(phone) < 10:
            raise forms.ValidationError("(*) Số điện thoại phải chứa ít nhất 10 chữ số.")
        phone_regex = r'^\d{10,11}$'
        if not re.match(phone_regex, phone):
            raise forms.ValidationError("(*) Số điện thoại không hợp lệ.")
        return phone