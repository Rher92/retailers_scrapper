from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max

from products.models import Product


class Command(BaseCommand):
    help = 'Delete Products duplicated'
    unique_fields = ['name']

    def handle(self, *args, **options):
        try:
            duplicates = (
                Product.objects.values(*self.unique_fields)
                .order_by()
                .annotate(max_id=Max('id'), count_id=Count('id'))
                .filter(count_id__gt=1)
            )

            _amount = len(duplicates)
            for duplicate in duplicates:
                (
                    Product.objects
                    .filter(**{x: duplicate[x] for x in self.unique_fields})
                    .exclude(id=duplicate['max_id'])
                    .delete()
                )    
        except Exception as e:
            raise CommandError(f'the action couldnt be executed due to: {e}')

        self.stdout.write(self.style.SUCCESS(f'Successfully! - Elements removed: {_amount}'))