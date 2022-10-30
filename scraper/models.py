from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=50)


class ProductSize(models.Model):
    name = models.CharField(max_length=50)


class Product(models.Model):
    product_url = models.CharField(max_length=250, unique=True)
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=500, null=True, blank=True)
    price = models.FloatField(default=0)
    rating = models.FloatField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    sizes = models.ManyToManyField(ProductSize)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class ProductImage(models.Model):
    image_url = models.CharField(max_length=250, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
