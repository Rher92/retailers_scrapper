from django.db import models
from utils.models import BaseCreatedUpdatedModel
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Price(BaseCreatedUpdatedModel):
    price = models.FloatField(
        null=False,
        blank=False,
        default=0.0        
    )

    def __str__(self):
        return f'{self.price}'


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
        max_length=30,
        null=True,
        blank=True,        
    )
    url = models.URLField(
        max_length=200,
        null=False,
        blank=False,        
    )
    product_unit = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    regular_price = models.ManyToManyField(
        Price, 
        related_name='regular_prices',
        related_query_name="regular_price",
        blank=True,        
    )        
    promotion_price = models.ManyToManyField(
        Price, 
        related_name='promotion_prices',
        related_query_name="promotion_price",
        blank=True,        
    )       
    card_promotion_price = models.ManyToManyField(
        Price, 
        related_name='card_promotion_prices',
        related_query_name="card_promotion_price",
        blank=True,        
    )     

    def __str__(self):
        return f'Name: {self.name} - SKU: {self.sku} - Django ID: {self.id}'