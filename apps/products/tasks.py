from celery import shared_task

from apps.common.parsers.enter import parsing_html, parsing_enter_categories, parsing_goods
from apps.common.parsers.panda_shop import parsing_panda_shop_html
from apps.common.parsers.insert_db import add_shop_category, add_shop_products


@shared_task(name="parse_enter_html", track_started=True)
def parse_enter_html(product_url: str, last_modify: str):
    parsing_html(product_url=product_url, last_modify=last_modify)


@shared_task(name="parse_enter", track_started=True)
def parse_enter():
    parsing_enter_categories()


@shared_task(name="parse_enter_goods", track_started=True)
def parse_enter_goods():
    parsing_goods()


@shared_task(name="add_shop_category", track_started=True)
def add_shop_category_task():
    add_shop_category()


@shared_task(name="add_shop_products", track_started=True)
def add_shop_products_task():
    add_shop_products()


@shared_task(name="parse_panda_shop_html", track_started=True)
def parse_panda_shop_html_task(product_url: str, last_modify: str):
    parsing_panda_shop_html(product_url=product_url, last_modify=last_modify)