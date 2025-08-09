from rest_framework import serializers
from django.db import transaction
from .models import Product,Collection,Review,Cart,CartItem

class CollectionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id','title','product_count']

    product_count = serializers.IntegerField(read_only=True)

class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','description','title','price','inventory','collection']
    
class ReviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id','date','name','description']

    def create(self, validated_data):
        with transaction.atomic():
            validated_data['product_id'] = self.context['product_id']
            return Review.objects.create(**validated_data)
    
class SimpleProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','price','collection']

class GetCartItemsSerializers(serializers.ModelSerializer):
    product = SimpleProductSerializers()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']

    def get_total_price(self,cartitem:CartItem):
        return cartitem.product.price * cartitem.quantity

         
class CartSerializers(serializers.ModelSerializer):
    items = GetCartItemsSerializers(many=True,read_only=True)
    class Meta:
        model = Cart
        fields = ['id','items','total_price']

    id = serializers.UUIDField(read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self,cart:Cart):
        return  sum([item.product.price * item.quantity for item in cart.items.all() ])
    
class AddCartItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product','quantity']

    def save(self, **kwargs):
        product = self.validated_data['product']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']

        try:
            cartitem = CartItem.objects.get(cart_id=cart_id,product=product)
            cartitem.quantity += quantity
            cartitem.save()
            self.instance = cartitem
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id,**self.validated_data)
        
        return self.instance