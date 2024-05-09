from django.db import models
from django.utils import timezone
import uuid
from core.helpers import formatCurrency
from django.contrib.auth.models import User
from sims.common.choices import (
    PACK_CHOICES,
    CATEGORY_CHOICES,
    STORE_TYPES,
    NHA_MANG_CHOICES,
    STATUS_CHOICES,
    REQUEST_CHOICES,
    STATUS_AR_CHOICES,
    TYPE_AR_CHOICES,
    PAY_METHOD_CHOICES,
    TRANSPORT_CHOICES,
    STATUS_PAY_CHOICES,
    INSTALLMENT_TYPE_CHOICES,
)
from django.contrib.postgres.fields import ArrayField

class SimStore(models.Model):
    id = models.CharField(primary_key=True, max_length=15)  # sim
    f = models.CharField(null=True, max_length=15, verbose_name="Số sim")
    f0 = models.IntegerField(null=True)
    f1 = models.IntegerField(null=True)
    f2 = models.IntegerField(null=True)
    f3 = models.IntegerField(null=True)
    f4 = models.IntegerField(null=True)
    f5 = models.IntegerField(null=True)
    f6 = models.IntegerField(null=True)
    f7 = models.IntegerField(null=True)
    f8 = models.IntegerField(null=True)
    f9 = models.IntegerField(null=True)
    pb = models.BigIntegerField(null=True, verbose_name="Giá bán")
    pn = models.BigIntegerField(null=True)  # gia
    t_detect = models.IntegerField(choices=NHA_MANG_CHOICES, null=True, verbose_name="Nhà mạng hệ thống")  # nha mang detect
    t = models.IntegerField(choices=NHA_MANG_CHOICES, null=True, verbose_name="Nhà mạng")  # nha mang
    d = models.BooleanField(default=False)  # xoa han
    c2 = models.IntegerField(choices=CATEGORY_CHOICES, null=True, verbose_name="Loại sim chính")  # danh muc chinh
    c = ArrayField(
        models.IntegerField(choices=CATEGORY_CHOICES), default=list, verbose_name="Loại sim"
    )  # danh muc
    h = models.BooleanField(default=False, verbose_name="Ẩn số sim khỏi web")  # xoa tam thoi
    tt = models.IntegerField(choices=PACK_CHOICES, null=True, blank=True, verbose_name="Loại mạng")  # tra truoc
    k = models.CharField(null=True, blank=True, verbose_name="Gói cước")  # goi cuoc
    ip = ArrayField(models.IntegerField(null=True), blank=True, null=True, verbose_name="Mua trả góp") # Installment purchase
    it = ArrayField(models.IntegerField(null=True), blank=True, null=True, verbose_name="Thời hạn trả góp") # Installment term
    iir = models.IntegerField(blank=True, null=True, verbose_name="Lãi suất trả góp") # Installment interest rate
    lpi = models.IntegerField(blank=True, null=True, verbose_name="Lãi suất trả chậm") # Late payment interest
    installment_type = models.IntegerField(choices=INSTALLMENT_TYPE_CHOICES.choices, blank=True, null=True, verbose_name="Loại trả góp")
    comment = models.JSONField(null=True, blank=True, default=dict, verbose_name="Comment giữ số")
    note = models.CharField(null=True, blank=True, verbose_name="Ghi chú")  # ghi chu
    publish = models.DateTimeField(auto_now=True, verbose_name="Thời gian update")
    @property
    def pb_format(self):
        return formatCurrency(self.pn)
    @property
    def telcoText(self):
        telco = dict(NHA_MANG_CHOICES).get(self.t, '')
        if self.t and self.t_detect and self.t != self.t_detect:
            return f"{telco} (CMGS)"
        return telco

    @property
    def categoryText(self):
        return dict(CATEGORY_CHOICES).get(self.c2, '')
    
    @property
    def packText(self):
        return dict(PACK_CHOICES).get(self.tt, 'Không xác định')
    
    @property
    def excelPackText(self):
        if self.tt:
            if self.tt == 1:
                return 'TT'
            else: 
                return 'TS'            
        else:
            return ''
    
    @property
    def get_category_names(self):
        return [dict(CATEGORY_CHOICES)[item] for item in self.c]

    def __str__(self):
        return self.id
    def save(self, *args, **kwargs):
        if self.pk:
            self.pn = self.pb
        
        super().save(*args, **kwargs)

class SimOrder(models.Model):
    def generate_unique_code():
        timestamp_part = timezone.now().strftime("%y%m%d")
        random_part = uuid.uuid4().hex[:8].upper()  # Random 8 alphanumeric characters
        return f"{timestamp_part}{random_part}"
    
    def default_created_at():
        return timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    store_type_choices = [
            choice for choice in STORE_TYPES.choices
            if choice[0] != STORE_TYPES.KHO_MIX
        ]
    code = models.CharField(max_length=20, default=generate_unique_code, unique=True, editable=False, verbose_name="Mã đơn hàng")
    sim = models.CharField(max_length=20, verbose_name="Số sim đặt mua")
    phone = models.CharField(max_length=20, verbose_name="Số điện thoại")
    amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Giá bán")
    name = models.CharField(max_length=50,verbose_name="Tên KH")
    address = models.TextField(max_length=300, null=True, blank=True, verbose_name="Địa chỉ")
    other_option = models.TextField(max_length=300, blank=True, null=True, verbose_name='Ghi chú đơn hàng')
    ip = models.GenericIPAddressField(blank=True, null=True)
    pushed =models.BooleanField(default=False, verbose_name="Push đơn")
    status = models.IntegerField(choices=STATUS_CHOICES.choices, default=STATUS_CHOICES.NEW, null=True, verbose_name="Trạng thái VC", help_text="Trạng thái vận chuyển")
    order_type = models.IntegerField(choices=REQUEST_CHOICES.choices, default=REQUEST_CHOICES.COMMON, null=True, verbose_name="Loại đơn")
    sale_notes = models.JSONField(default=dict)
    createdAt = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")
    updatedAt = models.DateTimeField(default=timezone.now)
    source_text = models.CharField(max_length=50, null=True, verbose_name="Nguồn đơn")
    sale_pic = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='orders', verbose_name="Nhân viên")
    store_type = models.IntegerField(choices=store_type_choices, help_text="Xác định số được đặt từ appsim hay từ kho sim", verbose_name="Kho nguồn")
    attributes = models.JSONField(null=True, blank=True, default=dict) # add more fields to order
    browse_history = models.TextField(null=True, blank=True)
    telco_id = models.IntegerField(choices=NHA_MANG_CHOICES, null=True,  verbose_name="Nhà mạng")
    c2 = models.IntegerField(choices=CATEGORY_CHOICES, null=True,  verbose_name="Loại sim")
    reason_text =  models.CharField(null=True, blank=True,  verbose_name="Lý do")
    transport = models.IntegerField(choices=TRANSPORT_CHOICES, null=True, blank=True, verbose_name="Giao vận")
    costs = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Chi phí")
    note_costs = models.CharField(null=True, blank=True,  verbose_name="Ghi chú chi phí")
    name_deliver = models.CharField(null=True, blank=True,  verbose_name="Người giao")
    phone_deliver = models.CharField(null=True, blank=True,  verbose_name="SĐT người giao")
    pay_kh_status = models.IntegerField(choices=STATUS_PAY_CHOICES.choices, null=True, blank=True, verbose_name="Trạng thái TT KH")
    pay_tho_status = models.IntegerField(choices=STATUS_PAY_CHOICES.choices, null=True, blank=True, verbose_name="Trạng thái TT Thợ")
    # default format of current time
    @property
    def defaultCreatedAt(self):
        return str(timezone.now())
    
    def __str__(self):
        return self.code

class AccountReceivable(models.Model):
    def generate_unique_code():
        timestamp_part = timezone.now().strftime("%y%m%d")
        random_part = uuid.uuid4().hex[:8].upper()  # Random 8 alphanumeric characters
        return f"{timestamp_part}{random_part}"

    code = models.CharField(primary_key=True, max_length=20, default=generate_unique_code, unique=True, editable=False, verbose_name="Mã")
    sim_order = models.ForeignKey(SimOrder, db_index=True, on_delete=models.CASCADE)
    created_userpay = models.DateField(default=timezone.now, verbose_name="Ngày TT")
    method_pay = models.IntegerField(choices=PAY_METHOD_CHOICES.choices, default=PAY_METHOD_CHOICES.CASH, null=True, verbose_name="Kiểu TT")
    user_create = models.CharField(null=True, blank=True,  verbose_name="Người tạo")
    # neu sim tra gop thi amount_payment la so tien goc
    amount_payment = models.BigIntegerField(null=True, blank=True, verbose_name="Số tiền")
    amount_interest= models.BigIntegerField(null=True, blank=True, verbose_name="Tiền lãi")
    amount_remaining = models.IntegerField(null=True, blank=True, verbose_name="Gốc còn lại")
    amount_interest_temp= models.BigIntegerField(null=True, blank=True, verbose_name="Lãi tạm tính")
    created_at = models.DateField(default=timezone.now, verbose_name="Ngày tạo")
    status = models.IntegerField(choices=STATUS_AR_CHOICES.choices, default=STATUS_AR_CHOICES.NEW, null=True, verbose_name="Trạng thái")
    type = models.IntegerField(choices=TYPE_AR_CHOICES.choices, default=TYPE_AR_CHOICES.THO, null=True, verbose_name="Loại")
    comment = models.TextField(null=True, blank=True, verbose_name="Ghi chú")
    attach_file = models.ImageField(null=True, blank=True, upload_to="account_receivable", verbose_name="Đính kèm")
    def __str__(self):
        return self.code
class UserProfile(models.Model):

    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    assign_order = models.BooleanField(default=False)
    is_current_assign = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username