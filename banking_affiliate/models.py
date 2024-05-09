from django.db import models
from django.utils import timezone
from .constants import TRANS_STATUS_CHOICES
class Transaction(models.Model):
    transaction_code=models.CharField(null=False, blank=False, max_length=15)
    sim=models.CharField(null=False, blank=False, max_length=15)
    amount= models.DecimalField(null=True, blank=True, max_digits=15, decimal_places=0)
    cif= models.CharField(null=True, blank=True, max_length=32)
    description= models.CharField(null=True, blank=True, max_length=255)
    merchant= models.CharField(null=True, blank=True, max_length=255)
    status = models.CharField(null=True, blank=True, max_length=16)
    address   = models.CharField(null=True, blank=True, max_length=255)
    name    = models.CharField(null=True, blank=True, max_length=120)
    phone   = models.CharField(null=True, blank=True, max_length=15)
    source   = models.CharField(null=True, blank=True, max_length=16)
    session_id   = models.CharField(null=True, blank=True, max_length=32)
    browse_history = models.TextField(null=True, blank=True)
    sim_full = models.CharField(null=True, blank=True, max_length=30)
    ip = models.CharField(null=True, blank=True, max_length=15)
    sim_info = models.TextField(null=True, blank=True)
    prepay  = models.IntegerField(null=True, blank=True, help_text="Tổng tiền thanh toán trước")
    payment_on_delivery  = models.IntegerField(null=True, blank=True, help_text="Số tiền thanh toán còn lại")
    price= models.DecimalField(null=True, blank=True, max_digits=15, decimal_places=0, help_text="Gia gốc")
    price_calc= models.DecimalField(null=True, blank=True, max_digits=15, decimal_places=0, help_text="Gía bán sau khi áp dụng chính sach giảm giá nếu có")
    user_id = models.IntegerField(null=True, blank=True, help_text="Customer Id")
    packageName = models.CharField(null=True, blank=True, max_length=20)
    attributes = models.JSONField(null=True, blank=True, default=dict) # add more fields to order
    createdAt = models.DateTimeField(default=timezone.now)
    updatedAt = models.DateTimeField(default=timezone.now)

    def isCompleted (self):
        return self.status == TRANS_STATUS_CHOICES.PAID or self.status == TRANS_STATUS_CHOICES.MOVED_TO_ORDER
	
class Customer(models.Model):
    cif=models.CharField(null=False, blank=False, max_length=15)
    sessionId= models.CharField(null=True, blank=True, max_length=40)
    login_token=models.CharField(null=True, blank=True, max_length=200)
    fullname= models.CharField(null=True, blank=True, max_length=255)
    mobile= models.CharField(null=True, blank=True, max_length=15)
    source= models.CharField(null=True, blank=True, max_length=10)
    createdAt = models.DateTimeField(default=timezone.now)
    updatedAt = models.DateTimeField(default=timezone.now)