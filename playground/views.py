from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from templated_mail.mail import BaseEmailMessage
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
from django.db import transaction, connection
from django.contrib.contenttypes.models import ContentType
from store.models import Product, OrderItem, Order, Customer, Collection
from tags.models import TaggedItem
from .tasks import notify_customers
import requests
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework.views import APIView
import logging


# @transaction.atomic()
# @cache_page(5 * 60)
# def say_hello(request):
# query_set[0:5]
# list(query_set)
# for product in query_set:
#     print(product)

# queryset = Product.objects.filter(unit_price__range=(20, 30))
# queryset = Product.objects.filter(collection__id__range=(1, 2, 3))
# queryset = Product.objects.filter(title__icontains="coffee")
# queryset = Product.objects.filter(last_update__year=2021)
# queryset = Product.objects.filter(description__isnull=True)

# queryset = Product.objects.filter(inventory__lt=10, unit_price__lt=20) # and operator
# queryset = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20) # and operator
# queryset = Product.objects.filter(

# Q Object
# queryset = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))  # or operator
# queryset = Product.objects.filter(Q(inventory__lt=10) & ~Q(unit_price__lt=20))  # not operator

# F Object
# queryset = Product.objects.filter(inventory=F('unit_price'))

# - desc order
# queryset = Product.objects.order_by("unit_price", "-title").reverse()

# Sorting
# product = Product.objects.order_by("unit_price")[0] # pick the first
# product = Product.objects.earliest("unit_price")

# Limiting Results
# queryset = Product.objects.all()[:5]  # 0,1,2,3,4
# queryset = Product.objects.all()[5:10]  # 5,6,7,8,9

# Selecting Fields
# queryset = Product.objects.values("id", "title", "collection__title")  # inner join
# queryset = Product.objects.values_list("id", "title", "collection__title")
# queryset = Product.objects.filter(id__in=OrderItem.objects.values("product_id").distinct()).order_by("title")

# Deferring Fields
# queryset = Product.objects.only("id", "title")  # careful many queries
# queryset = Product.objects.defer("description")

# Selecting Related Objects
# select_related (1)
# queryset = Product.objects.select_related("collection__someOtherField").all()  # inner join
# prefetch_related (n)
# queryset = Product.objects.prefetch_related("promotions").select_related("collection").all()
# queryset = Order.objects.select_related("customer").prefetch_related("orderitem_set__product").order_by("-placed_at")[:5]

# Aggregate Objects
# result = Product.objects.filter(collection__id=2).aggregate(count=Count("id"), min_price=Min("unit_price"))

# Annotating Objects
# queryset = Customer.objects.annotate(is_new=Value(True))
# queryset = Customer.objects.annotate(new_id=F("id") + 1)
# queryset = Customer.objects.annotate(full_name=Func(F("first_name"), Value(" "), F("last_name"), function="CONCAT"))
# queryset = Customer.objects.annotate(full_name=Concat("first_name", Value(" "), "last_name"))

# Grouping Data
# queryset = Customer.objects.annotate(orders_count=Count("order"))

# Expression Wrapper
# queryset = Product.objects.annotate(discounted_price=F("unit_price") * 0.8)
# discounted_price = ExpressionWrapper(F("unit_price") * 0.8, output_field=DecimalField())
# queryset = Product.objects.annotate(discounted_price=discounted_price)

# Querying Generic Relationships
# content_type = ContentType.objects.get_for_model(Product)  # represents the row of product model in django_content_type table
# queryset = TaggedItem.objects.select_related("tag") \
#                              .filter(content_type=content_type, object_id=1)

# Custom Managers
# TaggedItem.objects.get_tags_for(Product, 1)

# QuerySet Cache
# queryset = Product.objects.all()
# queryset[0]
# list(queryset)

# Creating Objects
# collection = Collection()
# collection.title = "Video Games"
# collection.featured_product = Product(pk=1)  # same as collection.featured_product_id = 1
# collection.save()
# collection = Collection.objects.create(name="a", featured_product_id=1)  # same as the four lines above

# Updating Objects
# collection = Collection(pk=11)
# collection.title = "Games"
# collection.featured_product = None
# collection.save()
# collection = Collection.objects.get(pk=11)
# collection.featured_product = Product(pk=1)
# collection.save()
# Collection.objects.filter(pk=11).update(featured_product=None)

# Deleting Objects
# collection = Collection(pk=11)
# collection.delete()
# collection.objects.filter(id__gt=5).delete()

# Transactions
# with transaction.atomic():
#     order = Order()
#     order.customer_id = 1
#     order.save()

#     item = OrderItem()
#     item.order = order
#     item.product_id = -1
#     item.quantity = 1
#     item.unit_price = 10
#     item.save()

# Executing Raw SQL Queries
# queryset = Product.objects.raw("SELECT id, title FROM store_product")
# with connection.cursor() as cursor:
#     cursor.execute("")
#     cursor.callproc("get_customers", [1, 2, 'a'])  # sp

# return HttpResponse("Hello World")
# return render(request, "hello.html", {"name": "Oykun", "orders": list(queryset)})
# return render(request, "hello.html", {"name": "Oykun", "result": list(queryset)})
# return render(request, "hello.html", {"name": "Oykun", "tags": list(queryset)})
# return render(request, "hello.html", {"name": "Oykun"})

### Sending Emails Section ###
# try:
#     # send_mail('subject', 'message', 'info@buybuy.com', ['bob@buybuy.com'])
#     # mail_admins('subject', 'message', html_message='message')

#     # message = EmailMessage('subject', 'message', 'from@buybuy.com', ['john@buybuy.com'])
#     # message.attach_file('playground/static/images/dog.jpg')
#     # message.send()

#     message = BaseEmailMessage(
#         template_name='emails/hello.html',
#         context={'name': 'Oykun'}
#     )
#     message.send(['john@buybuy.com'])

# except BadHeaderError:
#     pass
### Sending Emails Section ###

### Running Background Tasks Section ###
# notify_customers.delay('Hello')
### Running Background Tasks Section ###

### Caching Section ###
# key = 'httpbin_result'
# if cache.get(key) is None:
#     response = requests.get('https://httpbin.org/delay/2')
#     data = response.json()
#     cache.set(key, data)

# response = requests.get('https://httpbin.org/delay/2')
# data = response.json()

# return render(request, "hello.html", {"name": cache.get(key)})
# return render(request, "hello.html", {"name": data})

### Caching Section ###

# return render(request, "hello.html", {"name": "Oykun"})

### Caching Section ###
# class HelloView(APIView):
#     @method_decorator(cache_page(2 * 60))
#     def get(self, request):
#         response = requests.get('https://httpbin.org/delay/2')
#         data = response.json()
#         return render(request, "hello.html", {"name": "Oykun"})
### Caching Section ###

logger = logging.getLogger(__name__)


class HelloView(APIView):
    def get(self, request):
        try:
            logger.info('Calling httpbin')
            response = requests.get('https://httpbin.org/delay/2')
            logger.info('Received the response')
            data = response.json()
        except requests.ConnectionError:
            logger.critical("hhtpbin is offline")

        return render(request, "hello.html", {"name": "Oykun"})
