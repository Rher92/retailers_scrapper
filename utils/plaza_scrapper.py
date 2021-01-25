import time
import os
import pickle
import json
import requests
import threading
from concurrent.futures import Future

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display

from .decorators import timer
from products.tasks import save_instance


def get_links(browser):
    URL = os.environ.get('URL')
    SEEING_ALL = os.environ.get('SEEING_ALL')
    SEEING_ALL_SUPERMERCADO = os.environ.get('SEEING_ALL_SUPERMERCADO')
    SCROLL_PAUSE_TIME = os.environ.get('SCROLL_PAUSE_TIME')
    ITEM_SUPERMERCADO = os.environ.get('ITEM_SUPERMERCADO')

    links = []

    browser.get(URL)

    time.sleep(60)

    popup_window_button = browser.find_element_by_id('onesignal-slidedown-cancel-button')
    if popup_window_button:
        popup_window_button.click()

    time.sleep(5)
    menu=browser.find_elements_by_class_name('Header__info__left__item')[0]
    menu.click()

    categorias=browser.find_elements_by_class_name('MainMenu__wrapper__departments__item')

    action = ActionChains(browser)

    first_categories_text = [category.text for category in categorias if category.text != '']
    seeing_all = [SEEING_ALL, SEEING_ALL_SUPERMERCADO]
    for categoria in categorias:
        time.sleep(10)
        if categoria.text != '':
            action.move_to_element(categoria).click().perform()
            if categoria.text == ITEM_SUPERMERCADO:
                menues=browser.find_elements_by_class_name('MainMenu__wrapper__departments__item__link')
                menues_filter = [menu for menu in menues if menu.text != '' and menu.text not in first_categories_text and menu.text not in seeing_all]
                
                for menu in menues_filter:
                    menu.click()
                    time.sleep(10)
                    subcategories = browser.find_elements_by_class_name('MainMenu__wrapper__subcategories__item__sublink')
                    for subcategory in subcategories:
                        links.append(subcategory.get_property('href'))
                    return_button=browser.find_elements_by_class_name('pvaicon-ico-back-arrow')[1].click()
                    action.move_to_element(categoria).click().perform()
                    time.sleep(10)
                
                links = list(set(links))
            else:
                elements = browser.find_elements_by_class_name('MainMenu__wrapper__subcategories__item__sublink')
                for element in elements:
                    links.append(element.get_property('href'))
                links = list(set(links))

    categories_links = list(set(links))

    return links


# walk into the infinitive scroll unti 1200 items
def get_scroll_page(browser, link):
    items_links = []
    i = 1
    browser.get(link)
    time.sleep(5)
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        last_location_item = int(browser.find_elements_by_class_name('seen-element')[-1].location['y'])
        browser.execute_script(f"window.scrollTo(0, {last_location_item});")

        time.sleep(5)

        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            all_items = browser.find_elements_by_class_name('Showcase__link')
            items_links = [item.get_property('href') for item in all_items]
            break
        last_height = new_height

    return items_links


def fetch_item(link):
    future = Future()
    thread = threading.Thread(
        target=(lambda: future.set_result(generate_request(link)))) 
    thread.start()
    return future


def generate_request(link):
    _return = None
    response = requests.get(link)
    if response.status_code == 200:
        _return = response
    return _return    


def parse_info(future):
    response = future.result()
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

    json_instance = {
        'sku': sku,
        'name': name,
        'ean': ean,
        'regular_price': regular_price,
        'promotion_price': promotion_price,
        'url': url
    }

    json_instance = json.dumps(json_instance)
    save_instance.delay(json_instance)
    print(f'sku:{sku} - name:{name} - ean:{ean} - regular_price:{regular_price} - promotion_price: {promotion_price}')

@timer
def start_plazavea():
    items_sent = 0
    browser = None
    with Display():
        try:
            opts = FirefoxOptions()
            opts.add_argument("--width=1920")
            opts.add_argument("--height=1080")
            browser = webdriver.Firefox(firefox_options=opts)
            links = get_links(browser)
            for link in links:
                print(f'counter partial:{items_sent}')
                try:
                    items_links = get_scroll_page(browser, link)
                except Exception as e:
                    print(e)
                else:
                    for item_link in items_links:
                        future = fetch_item(item_link)
                        future.add_done_callback(parse_info)
                        items_sent += 1
                        while True:
                            if future.done:
                                break
            print(f'finish here!- number of items: {items_sent}')
        finally:
            if browser:
                browser.quit()

