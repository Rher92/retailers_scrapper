from django.db import models
from utils.models import BaseCreatedUpdatedModel
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Product(BaseCreatedUpdatedModel):
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,        
    )
    sku = models.CharField(
        max_length=30,
        null=True,
        blank=True,        
    )
    ean = models.CharField(
        max_length=100,
        null=True,
        blank=True,        
    )
    regular_price = models.FloatField(
        null=False,
        blank=False,
        default=0.0        
    )
    promotion_price = models.FloatField(
        null=False,
        blank=False,
        default=0.0        
    )
    url = models.URLField(
        max_length=200,
        null=False,
        blank=False,        
    )
    weight_unit = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        default=None
    )
    price_weight_unit = models.FloatField(
        null=False,
        blank=False,
        default=0.0        
    )

    def __str__(self):
        return f'name: {self.name} - ean: {self.ean}'
