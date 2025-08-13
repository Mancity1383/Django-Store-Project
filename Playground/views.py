from django.shortcuts import render
from django.db.models import Q,F,Value
from django.db import transaction,connection
from store.models import Product,OrderItem,Order,Collection
from tags.models import Tag,TaggedItem
from .tasks import send_kiss
# Create your views here.


def say_hello(request):
    send_kiss.delay("Ali")
    return render(request,'hello.html')