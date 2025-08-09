from django_filters import FilterSet
from .models import  Product

class ProductFIlters(FilterSet):
    class Meta:
        model = Product
        fields = {
            'collection_id':['exact'],
            'price': ['lt', 'gt'],
        }
