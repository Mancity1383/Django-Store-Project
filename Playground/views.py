from django.shortcuts import render
from django.db.models import Q,F,Value
from django.db import transaction,connection
from store.models import Product,OrderItem,Order,Collection
from tags.models import Tag,TaggedItem
# Create your views here.


def say_hello(request):
    # with transaction.atomic():
    #     tag = Tag()
    #     tag.pk  = 1
    #     tag.title = 'Love'
    #     tag.save()

    #     taggeditem = TaggedItem()
    #     taggeditem.tag = tag
    #     taggeditem.content_object = Product.objects.get(pk=12)
    #     taggeditem.save()

    return render(request,'hello.html')