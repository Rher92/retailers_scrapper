import pickle

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .serializers import ProductSerializer
from .models import Product

class ProductViewSet(viewsets.ViewSet):
    lookup_field = 'sku'
    
    def retrieve(self, request, sku=None):
        product = cache.get(sku)
        if not product:
            queryset = Product.objects.filter()
            product = get_object_or_404(queryset, sku=sku)
            product_pickled = pickle.dumps(product)
            cache.set(sku, product_pickled)
        else:
            product = pickle.loads(product)
            
        serializer = ProductSerializer(product)
        return Response(serializer.data)
