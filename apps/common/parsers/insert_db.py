__all__ = [
    'add_shop_category',
    'add_shop_products'
]

import json
import os
import time

from auditlog.models import LogEntry
from dictdiffer import diff
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from apps.common.helpers import logging
from apps.products.models import (
    ShopCategory,
    ShopProduct,
    Shop
)

directory = f'{settings.BASE_DIR}/media'


def add_shop_category() -> None:
    for file in os.listdir(directory):
        shop_name = os.fsdecode(file)
        for filename in os.listdir(f'{directory}/{shop_name}'):
            if 'items' in filename:
                start = time.process_time()
                with open(f'media/{shop_name}/{filename}', encoding='utf-8') as fp:
                    data = []
                    category_items = json.load(fp)
                for item_name in category_items:
                    try:
                        shop_queryset = Shop.objects.get(title=shop_name).id
                        data.append(ShopCategory(name=item_name, shop_id=shop_queryset))
                    except Shop.DoesNotExist:
                        raise ValueError('Shop not found')
                ShopCategory.objects.bulk_create(objs=data, ignore_conflicts=True)
                logging(message='Categories added', execution_time=time.process_time() - start)
    logging(message='Ended successfully')


def add_shop_products() -> None:
    for file in os.listdir(directory):
        shop_name = os.fsdecode(file)
        for filename in os.listdir(f'{directory}/{shop_name}'):
            if 'items' in filename:
                start = time.process_time()
                with open(f'media/{shop_name}/{filename}', encoding='utf-8') as fp:
                    category_items = json.load(fp)
                    data = []
                    label_data = []
                    data_for_check = {}
                    for category_name, category_data_value in category_items.items():
                        for category_data in category_data_value:
                            shop_category_queryset = list(ShopCategory.objects.filter(
                                name=category_name
                            ).values_list(
                                'id',
                                'category_id',
                                'shop_id',
                                'shop__title'
                            ))
                            for object_id, category_id, shop_id, shop_title in shop_category_queryset:
                                description = category_data.get('description')
                                title = category_data.get('title')
                                available = category_data.get('available')
                                last_modify = category_data.get('lastmod')
                                url = category_data.get('url')
                                price = float(''.join(str(category_data.get('price') or 0).split()))
                                label = category_data.get('label')
                                data_for_check[label] = {}
                                data.append(
                                    ShopProduct(
                                        label=label,
                                        title=title,
                                        description=description,
                                        price=price,
                                        available=available,
                                        shop_category_id=object_id,
                                        shop_id=shop_id,
                                        url=url,
                                        last_modify=last_modify,
                                        # category_id=category_id # Will be added in the future
                                    )
                                )
                                label_data.append(label)
                                data_for_check[label] = {
                                    'price': price,
                                    'available': available,
                                    'last_modify': last_modify
                                }
                        auditlog(data_for_check, label_data)
                        ShopProduct.objects.bulk_create(objs=data, ignore_conflicts=True)
                        ShopProduct.objects.bulk_update(objs=data, fields=['available', 'price', 'last_modify'])
                    logging(
                        message=f'Shop: {shop_name} - File: {filename} - added',
                        execution_time=time.process_time() - start
                    )
    logging(message='Ended successfully')


def auditlog(api_data: dict, label: list) -> None:
    queryset_dictionary_data = {}
    queryset_data = list(ShopProduct.objects.filter(
        label__in=label
    ).values(
        'label',
        'price',
        'available',
        'last_modify'
    ))
    if queryset_data:
        for data in queryset_data:
            queryset_dictionary_data[data.get('label')] = {}
            for _ in data.values():
                queryset_dictionary_data[data.get('label')] = {
                    'price': float(data.get('price')),
                    'available': data.get('available'),
                    'last_modify': data.get('last_modify')
                }
        differ = list(diff(first=queryset_dictionary_data, second=api_data))
        if differ:
            products_content = ContentType.objects.filter(
                app_label='products',
                model='shopproduct'
            ).last()
            for data in differ:
                if data[0] == 'change':
                    label = data[1].partition('.')[0]
                    field_changed = data[1].partition('.')[-1]
                    changes = data[2]
                    log = LogEntry(
                        object_pk=label,
                        changes=list(changes),
                        content_type=products_content,
                        object_repr=field_changed,
                        action=1
                    )
                    log.save()

        logging(message='Auditlog ended successfully')
    logging(message='Auditlog skipped - new data')
