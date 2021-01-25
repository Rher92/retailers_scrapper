import pickle
import json

from retailers_scrapper.celery import app
from .models import Product


@app.task(name='save_instance', autoretry_for=(Exception,), bind=True, retry_kwargs={'max_retries': 10, 'countdown': 5})
def save_instance(self, pickled_instance):
    json_instance = json.loads(pickled_instance)
    obj, created = Product.objects.update_or_create(
        name=json_instance['name'],
        defaults={
            'sku': json_instance['sku'],
            'ean': json_instance['ean'],
            'regular_price': json_instance['regular_price'],
            'promotion_price': json_instance['promotion_price'],
            'url': json_instance['url']
        }
    )

    _print = f'object updated: {obj.name}'
    if created:
        _print = f'object created: {obj.name}'
    print(_print)