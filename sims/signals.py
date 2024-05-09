from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SimOrder
from .utils import push_order_to_webhook, assignOrderToSale
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import UserProfile

@receiver(post_save, sender=SimOrder)
def sim_order_post_save(sender, instance, created, **kwargs):
    if created:
        try:
            assignOrderToSale(instance)
        except Exception as e:
            print("Error assignOrderToSale", e)
        try:
            push_order_to_webhook(instance)
        except Exception as e:
            print("Error push_order_to_webhook", e)
@receiver(post_save, sender=User)
def handle_user_creation(sender, instance, created, **kwargs):
    if created:
        # User created event
        print(f"User 2'{instance.username}' has been created.")
        UserProfile.objects.create(user=instance)
    else:
        # User update event
        print(f"User 1'{instance.username}' has been updated.")

@receiver(pre_delete, sender=User)
def handle_user_deletion(sender, instance, **kwargs):
    # User deletion event
    print(f"User '{instance.username}' is being deleted.")

# Connect the signal receivers
post_save.connect(handle_user_creation, sender=User)
pre_delete.connect(handle_user_deletion, sender=User)
