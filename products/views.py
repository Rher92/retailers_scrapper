from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .serializers import ProductSerializer
from .models import Product

class ProductViewSet(viewsets.ViewSet):
    lookup_field = 'sku'
    
    def retrieve(self, request, sku=None):
        # try to get from memcached
        queryset = Product.objects.filter()
        product = get_object_or_404(queryset, sku=sku)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
