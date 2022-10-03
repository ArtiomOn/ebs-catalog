import json
import os
import time
import typing

from auditlog.models import LogEntry
from dictdiffer import diff
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from apps.products.models import (
    ShopCategory,
    ShopProduct,
    Shop
)

__all__ = [
    'InsertDataBase'
]


class InsertDataBase:

    def __init__(self) -> None:
        self.directory = f'{settings.BASE_DIR}/media'

    @staticmethod
    def logging(
            message: str,
            data: typing.Union[str, list] = None,
            execution_time: typing.Optional[float] = None
    ) -> None:
        print(f'{message} | Data: {data} | Time: {execution_time} sec.')

    def add_shop_category(self) -> None:
        for file in os.listdir(self.directory):
            shop_name = os.fsdecode(file)
            for filename in os.listdir(f'{self.directory}/{shop_name}'):
                if 'items' in filename:
                    start = time.process_time()
                    with open(f'media/{shop_name}/{filename}', encoding='utf-8') as fp:
                        data = []
                        category_items = json.load(fp)
                    for item_name in category_items:
                        try:
                            shop_queryset = Shop.objects.get(
                                title=shop_name
                            ).id
                            data.append(
                                ShopCategory(
                                    name=item_name,
                                    shop_id=shop_queryset
                                ))
                        except Shop.DoesNotExist:
                            raise ValueError('Shop not found')
                    ShopCategory.objects.bulk_create(
                        objs=data,
                        ignore_conflicts=True
                    )
                    self.logging(
                        message='Categories added',
                        execution_time=time.process_time() - start
                    )
        self.logging(
            message='Ended successfully'
        )

    def add_shop_products(self) -> None:
        for file in os.listdir(self.directory):
            shop_name = os.fsdecode(file)
            for filename in os.listdir(f'{self.directory}/{shop_name}'):
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
                                    price = category_data.get('price')
                                    if isinstance(price, str):
                                        price = ''.join(price.split()[:-1])
                                    # noinspection PyArgumentList
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
                                            # category_id=category_id # Will be added in the future
                                        )
                                    )
                                    label_data.append(
                                        label
                                    )
                                    data_for_check[label] = {
                                        'price': float(str(price)),
                                        'available': available
                                    }
                            self.auditlog(data_for_check, label_data)
                            ShopProduct.objects.bulk_create(
                                objs=data,
                                ignore_conflicts=True
                            )
                            ShopProduct.objects.bulk_update(
                                objs=data,
                                fields=['available', 'price'],
                            )
                        self.logging(
                            message=f'Shop: {shop_name} - File: {filename} - added',
                            execution_time=time.process_time() - start
                        )
        self.logging(
            message='Ended successfully'
        )

    def auditlog(self, api_data: dict, label: list) -> None:
        # Get json data from DB
        queryset_dictionary_data = {}
        queryset_data = list(
            ShopProduct.objects.filter(
                label__in=label
            ).values(
                'label',
                'price',
                'available',
            ))
        if queryset_data:
            for data in queryset_data:
                queryset_dictionary_data[data.get('label')] = {}
                for _ in data.values():
                    queryset_dictionary_data[data.get('label')] = {
                        'price': float(data.get('price')),
                        'available': data.get('available')
                    }

            # Find difference
            differ = list(
                diff(
                    queryset_dictionary_data,
                    api_data
                )
            )
            if differ:
                # noinspection SpellCheckingInspection
                products_content = ContentType.objects.filter(
                    app_label='products',
                    model='shopproduct'
                ).last()
                for data in differ:
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

            self.logging(
                message='Auditlog ended successfully',
                data=differ
            )
        else:
            self.logging('Auditlog skipped - new data')
