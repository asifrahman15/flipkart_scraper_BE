from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from bs4 import BeautifulSoup
import requests

from scraper.models import Product, ProductImage, Category, ProductSize
from scraper.serializers import CategorySerializer, ImageSerializer, ProductSerializer
# Create your views here.


def scrape_data(product_url: str, product: Product = None):
    response = requests.get(product_url)
    if response.status_code == 200:
        htmlcontent = response.content
        soup = BeautifulSoup(htmlcontent, 'html.parser')

        if (not product) or (product.product_url == product_url):
            product, created = Product.objects.get_or_create(product_url=product_url)

        category = soup.find_all('a', attrs={'class': '_2whKao'})
        if category:
            product.category, created = Category.objects.get_or_create(name=category[1].text)

        title = soup.find('span', attrs={'class': 'B_NuCI'})
        product.title = title.text if title else "No Title Found"

        description = soup.find('div', attrs={'class': '_1AN87F'})
        product.description = description.text if description else "No Description Found"

        price = soup.find('div', attrs={'class': '_30jeq3 _16Jk6d'})
        if price:
            product.price = price.text.replace('₹', '').replace(',', '')
        else:
            product.price = 0

        rating = soup.select('._3LWZlK')
        product.rating = rating[0].text if rating else 0

        product.save()

        sizes = soup.find_all('a', attrs={'class': '_1fGeJ5 _2UVyXR _31hAvz'})
        for size in sizes:
            product.sizes.add(ProductSize.objects.get_or_create(name=size.text)[0])

        images = soup.find_all('img', attrs={'class': 'q6DClP'})
        SMALL_IMAGE_NUM, LARGE_IMAGE_NUM = '128', '832'

        if not images:
            images = soup.find_all('img', attrs={'class':'_396cs4 _2amPTt _3qGmMb _3exPp9'})

        for image in images:
            ProductImage.objects.get_or_create(image_url=image['src'].replace(SMALL_IMAGE_NUM, LARGE_IMAGE_NUM), product=product)

        return product
    else:
        return None


@api_view(['POST'])
def fetch_product(request):
    product_url = request.data.get('product_url')

    product_obj = Product.objects.filter(product_url=product_url)
    if product_obj.exists():
        product = product_obj[0]
        if product.updated_on + timedelta(days=7) < timezone.now():
            product = scrape_data(product_url, product=product)
    else:
        product = scrape_data(product_url)

    if not product:
        return Response({"error_msg":"Something wrong with the URL, please check again"}, status=400)

    return Response(ProductSerializer(instance=product).data, status=200)


@api_view(['GET', 'POST'])
def get_all_products(request):
    category_id = request.data.get('category_id')

    if (request.method == 'GET') or ((request.method == 'POST') and (not category_id)):
        products = Product.objects.all()
    elif request.method == 'POST':
        category = Category.objects.filter(id=category_id)
        if category.exists():
            products = Product.objects.filter(category=category[0])
        else:
            return Response({"error_msg":"Category Doesn't match with any existing category."}, status=404)
    else:
        return Response({"error_msg":"Only GET and POST methods are allowed."}, status=400)

    for product in products.filter(updated_on__lt=timezone.now() - timedelta(days=7)):
        scrape_data(product.product_url, product)

    return Response({"data": ProductSerializer(instance=products, many=True).data, "message": "The List of Products Fetched Successfuly the data are precise to 1 week."}, status=200)


@api_view(['GET'])
def get_all_categories(request):
    categories = Category.objects.all()

    return Response(CategorySerializer(instance=categories, many=True).data, status=200)