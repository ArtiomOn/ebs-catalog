from celery import shared_task
from apps.common.parsers.enter import EnterParser
from apps.common.parsers.foxmart import FoxmartParser
from apps.common.parsers.insert_db import InsertDataBase


@shared_task(name="parse_enter_categories", track_started=True)
def parse_enter_categories():
    EnterParser().get_categories()


@shared_task(name="parse_enter_products", track_started=True)
def parse_enter_products():
    EnterParser().get_products()


@shared_task(name="parse_foxmart_categories", track_started=True)
def parse_foxmart_categories():
    FoxmartParser().get_categories()


@shared_task(name="parse_foxmart_products", track_started=True)
def parse_foxmart_products():
    FoxmartParser().get_products()


@shared_task(name="insert_database_shop_category", track_started=True)
def insert_database_shop_category():
    InsertDataBase().add_shop_category()


@shared_task(name="insert_database_shop_product", track_started=True)
def insert_database_shop_product():
    InsertDataBase().add_shop_products()
