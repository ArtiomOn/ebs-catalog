from rest_framework.serializers import ModelSerializer

from apps.products.models import (
    Category,
    Comment,
    Shop,
    Attachment,
    ShopProduct,
    Product,
    Brand
)

__all__ = [
    'CategorySerializer',
    'CommentSerializer',
    'ShopSerializer',
    'ProductSerializer',
    'AttachmentSerializer',
    'ProductShopSerializer',
    'BrandSerializer',
]


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class BrandSerializer(ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class AttachmentSerializer(ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'


class ProductShopSerializer(ModelSerializer):
    class Meta:
        model = ShopProduct
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class BrandRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class CategoryRetrieveSerializer(ModelSerializer):
    attachment = AttachmentSerializer()

    class Meta:
        model = Category
        fields = "__all__"


class ProductRetrieveSerializer(ModelSerializer):
    attachment = AttachmentSerializer()
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = "__all__"


class ProductShopRetrieveSerializer(ModelSerializer):
    category = CategorySerializer()
    attachment = AttachmentSerializer()
    shop = ShopSerializer()
    product = ProductSerializer()
    shop_category = ProductShopSerializer

    class Meta:
        model = ShopProduct
        fields = "__all__"


class AttachmentRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Attachment
        fields = "__all__"


class CommentRetrieveSerializer(ModelSerializer):
    product = ProductSerializer()
    shop = ShopSerializer()

    class Meta:
        model = Comment
        fields = "__all__"


class ShopRetrieveSerializer(ModelSerializer):
    attachment = AttachmentSerializer()

    class Meta:
        model = Shop
        fields = "__all__"
