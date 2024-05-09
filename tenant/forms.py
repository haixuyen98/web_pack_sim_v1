from django import forms
from .models import Tenant
from django_tenants.utils import get_tenant_types
from core.settings import EMPTY_CHOICE

class TenantCloneForm(forms.ModelForm):
    allow_sale_via_bank = forms.BooleanField(widget=forms.CheckboxInput, required=False, label='Bán qua APP MB')
    allow_sync_appsim = forms.BooleanField(widget=forms.CheckboxInput, required=False, label="Kết nối với Appsim( đồng bộ dữ liệu đơn hàng về AppSIM)")
    allow_adjust_price_for_khosim = forms.BooleanField(widget=forms.CheckboxInput, required=False, label="Tùy chỉnh giá( áp dụng flashsale giảm giá kho cá nhân, ko tích không áp dụng giảm giá)")
    allow_adjust_price_for_appsim = forms.BooleanField(widget=forms.CheckboxInput, required=False, label="Tùy chỉnh giá giảm( áp dụng cả giảm giá kho appsim, ko tích chỉ áp dụng giá tăng)")
    class Meta:
        model = Tenant
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.config:
            config = self.instance.config
            allow_sale_via_bank_value = config.get('allow_sale_via_bank', None)
            if allow_sale_via_bank_value:
                self.fields['allow_sale_via_bank'].initial = allow_sale_via_bank_value
            allow_sync_appsim_value = config.get('allow_sync_appsim', None)
            if allow_sync_appsim_value:
                self.fields['allow_sync_appsim'].initial = allow_sync_appsim_value
            allow_adjust_price_for_khosim_value = config.get('allow_adjust_price_for_khosim', None)
            if allow_adjust_price_for_khosim_value:
                self.fields['allow_adjust_price_for_khosim'].initial = allow_adjust_price_for_khosim_value
            
            allow_adjust_price_for_appsim_value = config.get('allow_adjust_price_for_appsim', None)
            if allow_adjust_price_for_appsim_value:
                self.fields['allow_adjust_price_for_appsim'].initial = allow_adjust_price_for_appsim_value
            
            tenant_types = get_tenant_types()
            tenant_types = [(key, value['label']) for key, value in tenant_types.items() if key != 'public' and 'label' in value]
            tenant_types = EMPTY_CHOICE +tuple(tenant_types)
            self.fields['type'].choices = tenant_types
class TenantRegisterForm(TenantCloneForm):
    domain_prefix = forms.CharField(max_length=20, label='Tên domain (Viết liền không dấu) (*)')
    email = forms.CharField(required=True, label='Tạo tài khoản quản lý (Địa chỉ email) (*)')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Mật khẩu (Viết liền không dấu) (*)')
    class Meta:
        model = Tenant
        # fields = '__all__'
        fields = ('site_name','phone', 'type')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tenant_types = get_tenant_types()
        tenant_types = [(key, value['label']) for key, value in tenant_types.items() if key != 'public' and 'label' in value]
        tenant_types = EMPTY_CHOICE +tuple(tenant_types)
        self.fields['type'].choices = tenant_types
        
        self.fields['allow_sale_via_bank'].widget.attrs['hidden'] = True
        self.fields['allow_sale_via_bank'].label = ''
        
        self.fields['allow_sync_appsim'].widget.attrs['hidden'] = True
        self.fields['allow_sync_appsim'].label = ''
        
        self.fields['allow_adjust_price_for_khosim'].widget.attrs['hidden'] = True
        self.fields['allow_adjust_price_for_khosim'].label = ''
        
        self.fields['allow_adjust_price_for_appsim'].label = ''
        self.fields['allow_adjust_price_for_appsim'].widget.attrs['hidden'] = True
        
