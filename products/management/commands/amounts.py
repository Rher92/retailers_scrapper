from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max

from products.models import Product, Price

class Command(BaseCommand):
    help = 'Amount of products and prices'
    unique_fields_price = ['price']
    unique_fields_product = ['name']

    def handle(self, *args, **options):
        try:
            prices_duplicated = (
                Price.objects.values(*self.unique_fields_price)
                .order_by()
                .annotate(max_id=Max('id'), count_id=Count('id'))
                .filter(count_id__gt=1)
            )
            
            products_duplicated = (
                Product.objects.values(*self.unique_fields_product)
                .order_by()
                .annotate(max_id=Max('id'), count_id=Count('id'))
                .filter(count_id__gt=1)
            )

            print(f'Amount of Prices: {Price.objects.all().count()}')
            print(f'Amount without EAN: {Product.objects.filter(ean=None).count()}')
            print(f'Amount without SKU: {Product.objects.filter(sku=None).count()}')
            print(f'Amount of Products: {Product.objects.all().count()}')
            print(f'Amount of Plaza Vea products: {Product.objects.filter(url__icontains="plazavea").count()}')
            print(f'Amount of Tottus products: {Product.objects.filter(url__icontains="tottus").count()}')
            print(f'Amount of prices duplicated: {len(prices_duplicated)}')
            print(f'Amount of products duplicated: {len(products_duplicated)}')
        except Exception as e:
            raise CommandError(f'the action couldnt be executed due to: {e}')
        self.stdout.write(self.style.SUCCESS(f'Successfully!'))
