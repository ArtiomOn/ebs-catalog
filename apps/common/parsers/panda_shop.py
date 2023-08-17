import json
import os
from random import randrange
from time import sleep

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options
from slugify import slugify

from apps.common.helpers import logging, get_status

os.makedirs(f'{settings.PANDA_SHOP_ROOT}', exist_ok=True)
os.makedirs(f'{settings.PANDA_SHOP_HTML}', exist_ok=True)

webdriver_options = Options()
webdriver_options.add_argument("--no-sandbox")
webdriver_options.add_argument("--headless")
webdriver_options.add_argument("--disable-gpu")
webdriver_options.add_argument("--disable-dev-shm-usage")
webdriver_options.add_argument("headless")
driver = webdriver.Chrome(chrome_options=webdriver_options)


def parsing_panda_shop_categories() -> None:
    response = requests.get("https://www.pandashop.md/SitemapsProducts.ashx?lng=ro", allow_redirects=False)
    if not response.ok:
        raise RequestException(f"Error: {response.status_code}")

    xml = BeautifulSoup(response.text, 'lxml')

    products_url = xml.find_all('loc')

    for product_url in products_url:
        response = requests.get(product_url.text, allow_redirects=False)
        if not response.ok:
            continue

        xml = BeautifulSoup(response.text, 'html.parser')
        urls = xml.text.split('https://')[1:]
        full_url = ["https://" + url for url in urls]
        data = [{"url": url.rpartition('/')[0], "last_modify": url.rpartition('/')[2]} for url in full_url]
        for item in data:
            parsing_panda_shop_html(item['url'], item['last_modify'])
            # parse_panda_shop_html_task.apply_async(product_url=item['url'], last_modify=item['last_modify'])


def parsing_panda_shop_html(product_url: str, last_modify: str) -> None:
    sleep(randrange(4, 7))
    retries = 0
    while True:
        try:
            driver.get(product_url)
            with open(f'{settings.PANDA_SHOP_HTML}/{slugify(product_url)}.html', 'w+', encoding='utf-8') as file:
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


def parsing_panda_shop_goods():
    for filename in os.listdir(f'{settings.PANDA_SHOP_HTML}'):
        with open(f'{settings.PANDA_SHOP_HTML}/{filename}', encoding='utf-8') as fp:
            data = {}
            goods_data = BeautifulSoup(fp, 'html.parser')
            subcategory = goods_data.select_one('.breadcrumb > li:nth-child(4) > a > span').text
            data[subcategory] = []
            title = goods_data.select_one('.oneProd-titleMain').text.strip()

            table = goods_data.find('table', attrs={'class': 'width-xxs-100 width-sm-50'})
            category_data = []
            for row in table.find_all('tr'):
                category_name = row.find('td').get_text(strip=True)
                category_description = row.find_all('td')[1].get_text(strip=True)
                category_data.append(f"{category_name}: {category_description}")
            description = ", ".join(category_data)
            price = 0
            if goods_data.select_one('.price_curr'):
                price = goods_data.select_one('.price_curr').text.partition('\n')[0]
            lastmod = goods_data.select_one('last_modify').text
            label = slugify(f'enter, {title}, {description}, {price}, {lastmod}')
            url = goods_data.find('link', rel='alternate', hreflang='ro-md')['href']

            dictionary = {
                'label': label,
                'title': title,
                'description': description,
                'price': price,
                "lastmod": lastmod,
                'url': url,
                'available': bool(price)
            }
            data[subcategory].append(dictionary)
            logging(message=f"Product: {title} - saved")
        with open(f'{settings.PANDA_SHOP_ROOT}/panda_shop_items_{slugify(url)}.json', 'w+', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=5, ensure_ascii=False))
            logging(message=f"File: panda_shop_items_{slugify(url)}.json - saved")
