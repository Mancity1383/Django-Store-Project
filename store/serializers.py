from rest_framework import serializers
from django.db import transaction
from .models import Product,Collection,Review

class CollectionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id','title','product_count']

    product_count = serializers.IntegerField(read_only=True)

class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','price','collection']
    
class ReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id','date','name','description']

    def create(self, validated_data):
        with transaction.atomic():
            validated_data['product_id'] = self.context['product_id']
            return Review.objects.create(**validated_data)