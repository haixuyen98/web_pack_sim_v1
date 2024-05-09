from django.db import models

class SERVICE_PACKAGES(models.IntegerChoices):
    BASIC = 1, "Cơ bản"
    GOI_BAC = 2, "Gói Bạc"
    GOI_KC = 3, "Gói Kim Cương"

