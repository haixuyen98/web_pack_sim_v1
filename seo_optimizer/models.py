from django.db import models
from django.core.exceptions import ValidationError
from sims.common.choices import (
    CATEGORY_CHOICES,
    MIN_PRICES_RANGE,
    MAX_PRICES_RANGE
)

class SeoFile(models.Model):
  name = models.CharField(blank=False, null=False, max_length=200, verbose_name="Tên file")
  content = models.TextField(null=False, blank=False, verbose_name=" Nội dung")
  def __str__(self):
    return str(self.name)
class SeoProduct(models.Model):
  c2 = models.IntegerField(choices=CATEGORY_CHOICES, null=False, verbose_name="Loại sim")
  min_price = models.DecimalField(choices=MIN_PRICES_RANGE, null=True, blank=True, max_digits=15, decimal_places=0, verbose_name="Giá thấp nhất")
  max_price = models.DecimalField(choices=MAX_PRICES_RANGE, null=True, blank=True,max_digits=15, decimal_places=0, verbose_name="Giá cao nhất")
  title = models.CharField(null=False, blank=False, max_length=200, verbose_name="Tiêu đề")
  h1 = models.CharField(null=False, blank=False, max_length=200, verbose_name="Thẻ H1")
  description = models.TextField(null=False, blank=False, verbose_name="Mô tả")
  def __str__(self):
    return str(self.title)

  def clean(self):
    min_price = self.min_price
    max_price = self.max_price
    if min_price is not None and max_price is not None:
      if min_price > max_price:
          raise ValidationError(
              "min_price không được lớn hơn max_price"
          )
      super(SeoProduct, self).clean()

  class Meta:
    verbose_name="SEO chi tiết loại Sim"
