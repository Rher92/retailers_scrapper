from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet

app_name = 'products'

router = DefaultRouter()
router.register(r'', ProductViewSet, basename='products')

urlpatterns = router.urls

