from pathlib import Path

from auditlog.registry import auditlog
from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.db import models

from apps.common.models import BaseModel

__all__ = [
    'Comment',
    'Category',
    'ShopProduct',
    'Product',
    'Shop',
    'Attachment',
    'Brand',
    'ShopCategory'
]

User = get_user_model()


class Category(BaseModel):
    title = models.CharField(max_length=155)
    parent = models.ForeignKey(to='self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    languages = models.JSONField(blank=True, null=True)
    attachments = models.ManyToManyField('Attachment', related_name='category_attachments', blank=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['-id']

    def __str__(self):
        return self.title


class Product(BaseModel):
    title = models.CharField(max_length=155)
    category = models.ManyToManyField(Category)
    description = models.TextField()
    specification = models.JSONField(blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    languages = models.JSONField(blank=True, null=True)
    rating = models.IntegerField(
        default=0,
        blank=True,
        null=True,
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )
    attachments = models.ManyToManyField('Attachment', related_name='product_attachments', blank=True)
    verified = models.BooleanField(blank=True, null=True, default=False)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-id']

    def __str__(self):
        return self.title


class Comment(BaseModel):
    text = models.TextField()
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, blank=True, null=True)
    shop = models.ForeignKey(to='Shop', on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE)
    languages = models.JSONField(blank=True, null=True)
    attachments = models.ManyToManyField(to='Attachment', related_name='comment_attachments', blank=True)
    rating = models.IntegerField(
        default=0,
        blank=True,
        null=True,
        validators=[MaxValueValidator(5), MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-id']

    def __str__(self):
        return f'{self.id}'


class Shop(BaseModel):
    title = models.CharField(max_length=155)
    description = models.TextField(null=True, blank=True)
    shop_detail = models.JSONField(null=True, blank=True)
    languages = models.JSONField(blank=True, null=True)
    attachments = models.ManyToManyField('Attachment', related_name='shop_attachments', blank=True)

    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'
        ordering = ['-id']

    def __str__(self):
        return self.title


class ShopProduct(BaseModel):
    label = models.SlugField(primary_key=True, max_length=255)
    title = models.CharField(max_length=155)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    available = models.BooleanField(default=True)
    attachments = models.ManyToManyField('Attachment', related_name='product_shop_attachments', blank=True)
    last_modify = models.DateTimeField(null=True, blank=True)
    shop = models.ForeignKey(to=Shop, on_delete=models.CASCADE)
    languages = models.JSONField(blank=True, null=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, blank=True, null=True)
    shop_category = models.ForeignKey(to='ShopCategory', on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)
    verified = models.BooleanField(blank=True, null=True, default=False)
    url = models.URLField(blank=True, null=True, max_length=500)

    class Meta:
        verbose_name = 'Shop product'
        verbose_name_plural = 'Shop products'
        ordering = ['-label']

    def __str__(self):
        return self.title


class Brand(BaseModel):
    title = models.CharField(max_length=155)
    parent = models.ForeignKey(to='self', blank=True, null=True, on_delete=models.CASCADE, related_name='children')
    languages = models.JSONField(blank=True, null=True)
    attachments = models.ManyToManyField('Attachment', related_name='brand_attachments', blank=True)

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['-id']

    def __str__(self):
        return self.title


class ShopCategory(BaseModel):
    name = models.CharField(max_length=155)
    shop = models.ForeignKey(to=Shop, on_delete=models.CASCADE)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, blank=True, null=True)
    parent = models.ForeignKey(to='self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')

    class Meta:
        verbose_name = 'Shop category'
        verbose_name_plural = 'Shop categories'
        unique_together = ['shop', 'name']
        ordering = ['-id']

    def __str__(self):
        return self.name


class Attachment(BaseModel):
    title = models.CharField(max_length=75)
    file_url = models.FileField(blank=True)
    extension = models.CharField(max_length=10, blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    languages = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
        ordering = ['-id']

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.file_size = self.file_url.size
        self.extension = Path(self.file_url.name).suffix
        super(Attachment, self).save(force_insert, force_update, using, update_fields)


auditlog.register(Brand)
auditlog.register(ShopProduct)
auditlog.register(Shop)
auditlog.register(Product)
auditlog.register(Category)
auditlog.register(ShopCategory)
