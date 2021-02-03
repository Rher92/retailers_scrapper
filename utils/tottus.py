import time
import os
import pickle
import json
import requests
import threading
from concurrent.futures import Future
import concurrent.futures


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display

from .decorators import timer
from products.tasks import parse_instance_from_tottus


def get_links(browser):
    URL = os.environ.get('TOTTUS_URL')

    links = []
    browser.get(URL)

    time.sleep(30)

    modal_to_subscribe = browser.find_element_by_id('onesignal-slidedown-cancel-button')
    if modal_to_subscribe:
        modal_to_subscribe.click()

    time.sleep(7)
    
    modal_advertisement = browser.find_element_by_class_name('modal__close')
    if modal_advertisement:
        modal_advertisement.click()

    time.sleep(7)

    action = ActionChains(browser)

    categories_menu = browser.find_elements_by_class_name('category-title-container')
    for categorie in categories_menu:
        action.move_to_element(categorie).click().perform()
        time.sleep(7)
        if categorie.text == 'Supermercado':
            subcategories = browser.find_elements_by_css_selector('li.jsx-312510024.text.medium')
            for subcategorie in subcategories:
                links.append(subcategorie.find_element_by_css_selector('a.jsx-2300280587.null').get_property('href'))
        else:
            subcategories = browser.find_elements_by_class_name('see-all')
            for subcategorie in subcategories:
                links.append(subcategorie.get_property('href')) 
    
    links = list(set(links))
    return links


def fetch_pages(browser, link):
    items_links = []
    browser.get(link)
    action = ActionChains(browser)

    while True:
        time.sleep(7)

        products = browser.find_elements_by_class_name('product')
        for product in products:
            items_links.append(product.find_element_by_class_name('jsx-2300280587').get_property('href'))

        next_page_button = browser.find_elements_by_class_name('next')[1]
        if next_page_button.find_element_by_tag_name('a').get_attribute('aria-disabled') == 'true':
            break
        next_page_button.click()
    return items_links


@timer
def start_tottus():
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
                print(items_sent)
                try:
                    items_links = fetch_pages(browser, link)
                except Exception as e:
                    print(f'{link} - {e}')
                else:
                    for item_link in items_links:
                        json_instance = json.dumps(item_link)
                        parse_instance_from_tottus.delay(json_instance)
                        items_sent += 1                                               
        finally:
            if browser:
                browser.quit()
