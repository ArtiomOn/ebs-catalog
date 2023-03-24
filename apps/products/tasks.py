from celery import shared_task

from apps.common.parsers.enter import parsing_html, parsing_enter_categories


@shared_task(name="parse_enter_html", track_started=True)
def parse_enter_html(product_url: str, last_modify: str):
    parsing_html(product_url=product_url, last_modify=last_modify)


@shared_task(name="parse_enter", track_started=True)
def parse_enter():
    parsing_enter_categories()
