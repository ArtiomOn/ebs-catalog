import json
import os
from datetime import datetime
from random import randrange
from time import sleep

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from slugify import slugify

from apps.common.helpers import headers, cookies, get_status, logging
from apps.products.models import ShopProduct

shop_title = 'enter'

os.makedirs(f'{settings.ENTER_HTML}', exist_ok=True)
os.makedirs(f'{settings.ENTER_ROOT}', exist_ok=True)

webdriver_options = Options()
webdriver_options.add_argument("--no-sandbox")
webdriver_options.add_argument("--headless")
webdriver_options.add_argument("--disable-gpu")
webdriver_options.add_argument("--disable-dev-shm-usage")
webdriver_options.add_argument("headless")

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
driver = webdriver.Chrome(chrome_options=webdriver_options, desired_capabilities=caps)


def parsing_enter_categories() -> None:
    from apps.products.tasks import parse_enter_html
    response = requests.get("https://enter.online/sitemap.xml", headers=headers, cookies=cookies, allow_redirects=False)
    if not response.ok:
        raise RequestException(f"Error: {response.status_code}")

    xml = BeautifulSoup(response.text, 'xml')

    products_url = list(filter(None, xml.text.split('\n')))[7:]

    for product_url in products_url:
        sleep(randrange(4, 7))
        response = requests.get(product_url, headers=headers, cookies=cookies, allow_redirects=False)
        if not response.status_code == 200:
            continue

        xml = BeautifulSoup(response.text, 'xml')
        objects = xml.find_all('url')
        data_from_request = [url.loc.text for url in objects]
        existing_data = ShopProduct.objects.filter(url__in=data_from_request).values('url', 'last_modify')
        for obj in objects:
            if obj.loc.text in [item['url'] for item in existing_data] and '/ru/' not in obj.loc.text:
                permission = (
                        datetime.fromisoformat(obj.lastmod.text) <=
                        [item['last_modify'] for item in existing_data if item['url'] == obj.loc.text][0]
                )
                if not permission:
                    parse_enter_html.apply_async(
                        kwargs={
                            "product_url": obj.loc.text,
                            "last_modify": obj.lastmod.text
                        }, countdown=5)


def parsing_html(product_url: str, last_modify: str) -> None:
    retries = 0
    while True:
        try:
            sleep(randrange(3, 6))
            driver.get(product_url)
            with open(f'{settings.ENTER_HTML}/{slugify(product_url)}.html', 'w+', encoding='utf-8') as file:
                file.write(f'{driver.page_source} + <last_modify>{last_modify}</last_modify>')
                logging(message=f"File: {product_url}.html - saved", data=product_url)
            break
        except WebDriverException:
            retries += 1
            logging(
                message=f"Error: {WebDriverException}",
                data=f"Product url:{product_url}",
                retries=f"Retries: {retries}",
                status_code=get_status(driver.get_log('performance'))
            )
            sleep(randrange(3, 6))


def parsing_goods() -> None:
    for filename in os.listdir(f'{settings.ENTER_HTML}'):
        with open(f'{settings.ENTER_HTML}/{filename}', encoding='utf-8') as fp:
            data = {}
            goods_data = BeautifulSoup(fp, 'html.parser')

            subcategory = goods_data.select_one(".uk-breadcrumb > li:nth-child(2)").text.replace('\n', '')
            data[subcategory] = []
            lastmod = goods_data.select_one('last_modify').text
            price = 0
            if current_price := goods_data.select_one('.price-num > span'):
                price = current_price.text
            title = goods_data.select_one('.details-title').text
            description = goods_data.select_one('h1 > span:nth-child(2)').text
            url = goods_data.find('link', rel="canonical")['href']
            label = slugify(f'{shop_title}, {title}, {description}, {price}, {lastmod}')

            dictionary = {
                'label': label,
                'title': title,
                'description': description,
                'price': price,
                "lastmod": lastmod,
                'url': url,
                'available': not bool(goods_data.select_one('.uk-margin-small > p'))
            }
            data[subcategory].append(dictionary)
            logging(message=f"Product: {title} - saved")
        with open(f'{settings.ENTER_ROOT}/enter_items_{slugify(url)}.json', 'w+', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=5, ensure_ascii=False))
            logging(message=f"File: enter_items_{label}.json - saved")
