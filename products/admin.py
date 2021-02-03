from django.contrib import admin

from .models import Product, Price


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    pass