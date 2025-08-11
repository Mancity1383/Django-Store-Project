from rest_framework import serializers
from django.db import transaction
from .models import *
import re

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

    
class AddCartItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product','quantity']

    def save(self, **kwargs):
        with transaction.atomic():
            product : Product = self.validated_data['product']
            quantity = self.validated_data['quantity']
            cart_id = self.context['cart_id']
            
            if product.inventory >= quantity:
                print(product.inventory)
                try:
                    cartitem = CartItem.objects.get(cart_id=cart_id,product=product)
                    cartitem.quantity += quantity
                    cartitem.save()
                    self.instance = cartitem
                except CartItem.DoesNotExist:
                    self.instance = CartItem.objects.create(cart_id=cart_id,**self.validated_data)
                
                return self.instance
            
            else:
                raise serializers.ValidationError({
                    'quantity': f"The inventory of product {product.title} is {product.inventory}, requested {quantity}."
                })
    
class UpdateCartItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
         
class CartSerializers(serializers.ModelSerializer):
    items = GetCartItemsSerializers(many=True,read_only=True)
    class Meta:
        model = Cart
        fields = ['id','items','total_price']

    id = serializers.UUIDField(read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self,cart:Cart):
        return  sum([item.product.price * item.quantity for item in cart.items.all() ])

class CustomerSerializers(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['user_id','phone','birth_date','membership']

    # def save(self, **kwargs):
    #     user_id = self.context['user_id']

    #     try:
    #         customer = Customer.objects.get(user_id=user_id)
    #         for attr, value in self.validated_data.items():
    #             setattr(customer, attr, value)
    #         customer.save()
    #         self.instance = customer
    #     except Customer.DoesNotExist:
    #         self.instance = Customer.objects.create(user_id=user_id, **self.validated_data)

    #     return self.instance

class OrderItemSerializers(serializers.ModelSerializer):
    product = SimpleProductSerializers()
    class Meta:
        model = OrderItem
        fields =['id','product','quantity','unit_price']

class GETOrdersSerializers(serializers.ModelSerializer):
    items = OrderItemSerializers(many=True,read_only=True)
    customer = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Order
        fields = ['id','customer','placed_at','payment_status','items']

class POSTOrdersSerializers(serializers.ModelSerializer):
    cart_id = serializers.UUIDField()
    class Meta:
        model = Order
        fields = ['cart_id']

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise ValidationError("cart_id doesn't exist")
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']

            customer = Customer.objects.get(user_id=user_id)

            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            
            if cart_items.count() <= 0 :
                raise ValidationError({'items':"There is no item in this cart"})
            
            order = Order.objects.create(customer_id = customer.id)

            order_items = []
            products_to_update = []
            
            for item in cart_items:
                product = item.product
                quantity = item.quantity
                unit_price = product.price * quantity

                if product.inventory < quantity:
                    raise ValidationError({'quantity':f"Quantity Error for {product.title}"})

                order_items.append(OrderItem(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price
                ))
                
                product.inventory -= quantity
                products_to_update.append(product)
            
            OrderItem.objects.bulk_create(order_items)

            Product.objects.bulk_update(products_to_update, ['inventory'])

            Cart.objects.filter(pk=cart_id).delete()

            return order
