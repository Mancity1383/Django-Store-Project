from django.contrib.auth.models import User
from rest_framework import status
from model_bakery import baker
from store.models import Product,Collection,Cart,CartItem
from rest_framework.test import APIClient
import pytest


@pytest.mark.django_db
class TestPostCart:
    def test_if_any_user_can_get_cart_return_201(self):
        client = APIClient()
        response = client.post('/store/carts/')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] is not None
    
    def test_if_any_user_can_add_items_return_201_if_inventory_low_return_400(self):
        client = APIClient()
        cart = baker.make(Cart)
        product = baker.make(Product,inventory=2)
        #Add
        response = client.post(f'/store/carts/{cart.id}/items/',{'product':product.pk,'quantity':1})
        assert response.status_code == status.HTTP_201_CREATED
        #Update
        response = client.post(f'/store/carts/{cart.id}/items/',{'product':product.pk,'quantity':1})
        assert response.status_code == status.HTTP_201_CREATED
        #Low inventory
        response = client.post(f'/store/carts/{cart.id}/items/',{'product':product.pk,'quantity':3})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    
@pytest.mark.django_db
class TestGetCart:
    def test_if_any_user_can_get_items_return_200(self):
        client = APIClient()
        cart = baker.make(Cart)
        response = client.get(f'/store/carts/{cart.id}/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_if_any_user_can_add_items_return_200(self):
        client = APIClient()
        cart = baker.make(Cart)
        cartitem = baker.make(CartItem,cart=cart)
        response = client.get(f'/store/carts/{cart.id}/items/{cartitem.id}/')
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestUpadteCartItems:
    def test_if_any_user_can_update_items_return_200(self):
        client = APIClient()
        cart = baker.make(Cart)
        product = baker.make(Product,inventory=3)
        cartitem = baker.make(CartItem,product=product,cart=cart)
        response = client.patch(f'/store/carts/{cart.id}/items/{cartitem.id}/',{'quantity':3})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDeleteCartItems:
    def test_if_any_user_can_update_items_return_200(self):
        client = APIClient()
        cart = baker.make(Cart)
        product = baker.make(Product,inventory=3)
        cartitem = baker.make(CartItem,product=product,cart=cart)
        response = client.delete(f'/store/carts/{cart.id}/items/{cartitem.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
