from rest_framework import serializers
from .models import *
from store.models import Product
from store.serializers import SimpleProductSerializers
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

class TaggedItemSerilizers(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    product = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = TaggedItem
        fields = ['id','tag_id','product_id','product']

    def get_product(self,obj:TaggedItem):
        if isinstance(obj.content_object,Product):
            return SimpleProductSerializers(obj.content_object).data
        return None
    
    def create(self, validated_data):
        with transaction.atomic():
            product_id = validated_data['product_id']

            if Product.objects.filter(pk=product_id).exists():
                content_type = ContentType.objects.get_for_model(Product)
                return TaggedItem.objects.create(tag_id=self.context['tag_id'],content_type=content_type,object_id=product_id)
            raise serializers.ValidationError({'product_id_error':'product_id not exist'})



class TagSerilizers(serializers.ModelSerializer):
    items = TaggedItemSerilizers(read_only=True,many=True)
    tagged_item_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Tag
        fields = ['id','title','tagged_item_count','items']

