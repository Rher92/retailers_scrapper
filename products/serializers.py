from rest_framework import serializers

from .models import Product, Price


class LastPriceSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    modified = serializers.SerializerMethodField()

    class Meta:
        model = Price
        fields = '__all__'
    
    def get_price(self, obj):
        _return = None
        if obj.last():
            _return = f'{obj.last()}'
        return _return

    def get_modified(self, obj):
        _return = None
        if obj.last():
            _return = obj.last().modified
        return _return


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['created', 'price']


class ProductSerializer(serializers.ModelSerializer):
    regular_price = LastPriceSerializer()
    promotion_price = LastPriceSerializer()
    card_promotion_price = LastPriceSerializer()
    
    class Meta:
        model = Product
        fields = '__all__'


class ProductHistorialSerializer(serializers.ModelSerializer):
    regular_price = PriceSerializer(many=True, read_only=True)
    promotion_price = PriceSerializer(many=True, read_only=True)
    card_promotion_price = PriceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['regular_price', 'promotion_price', 'card_promotion_price']