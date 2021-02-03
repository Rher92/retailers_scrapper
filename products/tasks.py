import pickle
import json

from django.core import management
import requests
from bs4 import BeautifulSoup

from retailers_scrapper.celery import app
from .models import Product, Price


def save_instance(json_instance):
    product, created = Product.objects.update_or_create(
        name=json_instance['name'],
        defaults={
            'sku': json_instance['sku'],
            'ean': json_instance['ean'],
            'url': json_instance['url'],
            'product_unit': json_instance['product_unit'],
        }
    )

    _regular_price = json_instance.get('regular_price')
    if _regular_price:
        regular_price, _ = Price.objects.get_or_create(price=_regular_price)
        product.regular_price.add(regular_price)

    _promotion_price = json_instance.get('promotion_price')
    if _promotion_price:  
        promotion_price, _ =  Price.objects.get_or_create(price=_promotion_price)
        product.promotion_price.add(promotion_price)

    _card_promotion_price = json_instance.get('card_promotion_price')
    if _card_promotion_price:
        card_promotion_price, _ =  Price.objects.get_or_create(price=_card_promotion_price)
        product.card_promotion_price.add(card_promotion_price)

    _print = f'object updated: {product.name}'
    if created:
        _print = f'object created: {product.name}'
    print(_print)


@app.task(name='parse_instance', autoretry_for=(Exception,), bind=True, retry_kwargs={'max_retries': 3, 'countdown': 5})
def parse_instance_from_tottus(self, url):
    url = json.loads(url)
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts=soup.find_all('script')
        first_script = json.loads(scripts[0].string)

        for script in scripts:
            if 'ean' in str(script.string):
                script_string = script.string
                data_json = json.loads(script_string)
                prices_json = data_json['props']['pageProps']['data']['prices']
                sku =  data_json['props']['pageProps']['data']['sku']
                attributes_json = data_json['props']['pageProps']['data']['attributes']

        url = str(response.url)
        name = str(first_script.get('name'))
        regular_price = float(prices_json.get('regularPrice'))
        
        card_promotion_price = prices_json.get('cmrPrice')
        if card_promotion_price:
            card_promotion_price = float(card_promotion_price)

        promotion_price = None
        if prices_json.get('regularPrice') != prices_json.get('currentPrice'):
            promotion_price = float(prices_json.get('currentPrice'))

        _units = [attributes_json.get('unidad-de-medida'), attributes_json.get('formato')]
        measurement_unit = ' - '.join(_units)
        ean = str(attributes_json.get('ean'))

        json_instance = {
            'sku': sku,
            'name': name,
            'ean': ean,
            'regular_price': regular_price,
            'promotion_price': promotion_price,
            'url': url,
            'product_unit': measurement_unit,
            'card_promotion_price': card_promotion_price
        }

        save_instance(json_instance)
    else:
        raise Exception(f'Requests from {url} does not get status code: 200')


@app.task(name='parse_instance', autoretry_for=(Exception,), bind=True, retry_kwargs={'max_retries': 3, 'countdown': 5})
def parse_instance_from_plaza_vea(self, url):
    url = json.loads(url)
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts=soup.find_all('script')

        for script in scripts:
            if 'vtex.events.addData' in str(script.string):
                script_string = script.string
                parsed_string = script_string.strip().split('(')[1].split(')')[0]
                data_json_vtex = json.loads(parsed_string)
            elif 'vtxctx' in str(script.string):
                script_string = script.string
                parsed_string = script_string.strip().split('=')[1].strip().split(';')[0]
                data_json_vtxctx = json.loads(parsed_string)

        name = str(soup.select('.ProductCard__name')[0].find('div').text)
        ean = data_json_vtex.get('productEans')
        regular_price = float(data_json_vtex.get('productListPriceTo'))
        promotion_price = float(data_json_vtex.get('productPriceTo'))
        url = str(response.url)
        
        sku = data_json_vtex.get('productReferenceId')
        if not sku:
            sku = data_json_vtxctx.get('skus')

        if ean:
            ean = str(ean[0])

        if sku:
            sku = str(sku)

        measurement_unit = soup.find_all(class_='ProductCard__prices__title')[0]
        if measurement_unit:
            measurement_unit = measurement_unit.text

        card_promotion_price = None

        json_instance = {
            'sku': sku,
            'name': name,
            'ean': ean,
            'regular_price': regular_price,
            'promotion_price': promotion_price,
            'url': url,
            'product_unit': None, #measurement_unit,
            'card_promotion_price': card_promotion_price
        }        

        save_instance(json_instance)
    else:
        raise Exception(f'Requests from {url} does not get status code: 200')


@app.task(name='scrape_plaza_vea', autoretry_for=(Exception,), bind=True, retry_kwargs={'max_retries': 3, 'countdown': 5})
def scrape_plaza_vea():
    try:
        management.call_command("scrape_plaza_vea", verbosity=0)
        management.call_command("delete_products_duplicated", verbosity=0)
        management.call_command("delete_prices_duplicated", verbosity=0)
    except:
        print(e)


@app.task(name='scrape_tottus', autoretry_for=(Exception,), bind=True, retry_kwargs={'max_retries': 3, 'countdown': 5})
def scrape_tottus():
    try:
        management.call_command("scrape_tottus", verbosity=0)
        management.call_command("delete_products_duplicated", verbosity=0)
        management.call_command("delete_prices_duplicated", verbosity=0)        
    except:
        print(e)