import json
import os
from datetime import datetime
from random import randrange
from time import sleep
from typing import Optional

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from slugify import slugify

from apps.common.helpers import headers, cookies
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
driver = webdriver.Chrome(chrome_options=webdriver_options)


def logging(
        message: str,
        data: Optional[str] = None,
        execution_time: Optional[float] = None
) -> None:
    print(f"{message} | Data: {data} | Time: {execution_time} sec.")


def parsing_enter_categories() -> None:
    from apps.products.tasks import parse_enter_html
    response = requests.get("https://www.pandashop.md/SitemapsProducts.ashx?lng=ro", allow_redirects=False)
    if not response.ok:
        raise RequestException(f"Error: {response.status_code}")

    xml = BeautifulSoup(response.text, 'xml')

    products_url = xml.find_all('loc')

    for product_url in products_url:
        sleep(randrange(4, 7))
        response = requests.get(product_url.text, allow_redirects=False)
        if not response.status_code == 200:
            continue

        xml = BeautifulSoup(response.text, 'xml')
        objects = xml.find_all('url')
        for obj in objects:
            last_modified = existing_data.get(obj, None)
            if last_modified:
                datetime.fromisoformat(obj.lastmod.text)

            parse_enter_html.apply_async(product_url=[obj.loc.text], last_modify=[obj.lastmod.text], countdown=5)
