import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings

# Create your models here.

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.DecimalField(max_digits=5,decimal_places=2)

class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey('Product',on_delete=models.SET_NULL,null=True,blank=True,related_name='+')

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title']

class Product(models.Model):
    title = models.CharField(max_length=255,db_index=True)
    slug = models.SlugField(blank=True)
    description = models.TextField(null=True,blank=True)
    price = models.DecimalField(max_digits=6,decimal_places=2,validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection,on_delete=models.PROTECT,related_name='products')
    promotion = models.ManyToManyField(Promotion,blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title','price','inventory']

class Review(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_SILVER,'Silver'),
        (MEMBERSHIP_BRONZE,'Bronze'),
        (MEMBERSHIP_GOLD,'Gold')
    ]
    phone = models.CharField(max_length=20)
    birth_date = models.DateField(blank=True,null=True)
    membership = models.CharField(max_length=1,choices=MEMBERSHIP_CHOICES,default=MEMBERSHIP_BRONZE)
    user : AbstractUser = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    def first_name(self):
        return self.user.first_name
    
    def last_name(self):
        return self.user.last_name

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('P','Pending'),
        ('C','Complete'),
        ('F','Failed')
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1,choices=PAYMENT_CHOICES,default='P')
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT,related_name='orders')

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.PROTECT)
    product = models.ForeignKey(Product,on_delete=models.PROTECT,related_name='orderitems')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)

    def clean(self):
        if self.product and self.quantity:
            if self.quantity > self.product.inventory:
                raise ValidationError({'quantity': f'Only {self.product.inventory} available for "{self.product.title}".'})
    
    def save(self, *args, **kwargs):
        if self.product and self.quantity :
            self.unit_price = self.product.price *self.quantity
        super().save(*args, **kwargs)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip = models.CharField(max_length=255,null=True)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [['cart','product']]