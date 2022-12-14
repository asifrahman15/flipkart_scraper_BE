from rest_framework import serializers

from scraper.models import Product, Category, ProductImage


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField('_get_category')
    sizes = serializers.SerializerMethodField('_get_sizes')
    images = serializers.SerializerMethodField('_get_images')

    def _get_category(self, prod_obj: Product):
        return prod_obj.category.name if prod_obj.category else "No Category"

    def _get_sizes(self, prod_obj: Product):
        return [size.name for size in prod_obj.sizes.all()]

    def _get_images(self, prod_obj: Product):
        return [prod.image_url for prod in prod_obj.productimage_set.all()]

    class Meta:
        model = Product
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'