from django.contrib.auth.models import User
from rest_framework import status
from model_bakery import baker
from store.models import Product,Collection
from rest_framework.test import APIClient
import pytest

@pytest.mark.django_db
class TestPostProduct:
    def test_if_user_is_anonymous_return_401(self):
        client = APIClient()
        collection = baker.make(Collection)
        response = client.post('/store/products/',{'title':'test','price':10.00,'inventory':5,'collection':collection.id})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_auth_return_403(self):
        client = APIClient()
        client.force_authenticate(user={})
        collection = baker.make(Collection)
        response = client.post('/store/products/',{'title':'test','price':10.00,'inventory':5,'collection':collection.id})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_return_201(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        collection = baker.make(Collection)
        response = client.post('/store/products/',{'title':'test','price':10.00,'inventory':5,'collection':collection.id})
        assert response.status_code == status.HTTP_201_CREATED

    def test_if_data_title_is_invalid_return_400(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        collection = baker.make(Collection)
        response = client.post('/store/products/',{'title':'','price':10.00,'inventory':5,'collection':collection.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_price_is_invalid_return_400(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        collection = baker.make(Collection)
        response = client.post('/store/products/',{'title':'','price':-1,'inventory':5,'collection':collection.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_if_data_inventory_is_invalid_return_400(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        collection = baker.make(Collection)
        response = client.post('/store/products/',{'title':'','price':10,'inventory':-1,'collection':collection.id})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    

@pytest.mark.django_db
class TestRetriveProduct:
    def test_if_anonymous_user_can_get_product_return_200(self):
        client = APIClient()
        product = baker.make(Product)
        response = client.get(f'/store/products/{product.id}/')
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestUpdateProduct:
    def test_if_auth_user_can_update_product_return_403(self):
        client = APIClient()
        client.force_authenticate(user={})
        product = baker.make(Product)
        response = client.patch(f'/store/products/{product.id}/',{'title':'NOthing','price':5})
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_if_admin_user_can_update_product_return_403(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        product = baker.make(Product)
        response = client.patch(f'/store/products/{product.id}/',{'title':'NOthing','price':5})
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestDeleteProduct:
    def test_if_auth_user_can_delete_product_return_403(self):
        client = APIClient()
        client.force_authenticate(user={})
        product = baker.make(Product)
        response = client.delete(f'/store/products/{product.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_admin_user_can_delete_product_return_200(self):
            client = APIClient()
            client.force_authenticate(user=User(is_staff=True))
            product = baker.make(Product)
            response = client.delete(f'/store/products/{product.id}/')
            assert response.status_code == status.HTTP_204_NO_CONTENT