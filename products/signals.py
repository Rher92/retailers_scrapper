from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Product


@receiver(post_save, sender=Product)
def save_instance_into_cache(sender, instance, **kwargs):
    pass


@receiver(post_delete, sender=Product)
def remove_instance_into_cache(sender, instance, **kwargs):
    pass