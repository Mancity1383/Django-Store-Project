from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import status
from model_bakery import baker
from store.models import Cart,CartItem,Order,OrderItem,Customer,Product
from rest_framework.test import APIClient
import pytest

@pytest.mark.django_db
class TestPostOrder:
    def test_if_anonymous_can_post_order_retrun_401(self):
        client = APIClient()
        cart = baker.make(Cart)
        cartitem = baker.make(CartItem,cart=cart)
        response = client.post(f'/store/orders/',{'cart_id':cart.id})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_auth_can_post_order_retrun_201(self):
        client = APIClient()
        user = baker.make(settings.AUTH_USER_MODEL)
        client.force_authenticate(user=user)
        if not Customer.objects.filter(user=user).exists():
            customer = baker.make(Customer,user=user)
        else:
            customer = Customer.objects.get(user=user)
        cart = baker.make(Cart)
        product = baker.make(Product,inventory=3)
        inventory = product.inventory
        cartitem = baker.make(CartItem,product=product,cart=cart,quantity=1)
        response = client.post(f'/store/orders/',{'cart_id':cart.id})

        assert response.status_code == status.HTTP_200_OK

        response = client.get(f'/store/carts/{cart.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
class TestDeleteOrder:
    def test_if_auth_can_delete_order_retrun_403(self):
        client = APIClient()
        user = baker.make(settings.AUTH_USER_MODEL)
        if not Customer.objects.filter(user=user).exists():
            customer = baker.make(Customer,user=user)
        else:
            customer = Customer.objects.get(user=user)
        client.force_authenticate(user=user)
        order = baker.make(Order,customer=customer)

        response = client.delete(f'/store/orders/{order.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN
