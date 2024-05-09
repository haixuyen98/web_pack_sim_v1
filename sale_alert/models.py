from django.db import models
from datetime import timedelta
from django.utils import timezone

class SaleAlert(models.Model):
  vitual_names = models.CharField(null=False, blank=False, max_length=100)
  vitual_address = models.TextField(null=False, blank=False)
  vitual_sims = models.CharField(null=False, blank=False, max_length=20)
  vitual_times = models.CharField(null=False, blank=False, max_length=20)
  @property
  def message(self):
    times = timezone.now() + timedelta(seconds=int(self.vitual_times))
    return f'Khách hàng {self.vitual_names} ở {self.vitual_address} đã mua sim {self.vitual_sims} lúc {times.strftime("%Y-%m-%d")}.'