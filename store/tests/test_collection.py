from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from store.models import Collection,Product
from model_bakery import baker
import pytest

@pytest.mark.django_db
class TestCollection:
    def test_if_user_is_anonymous_return_401(self):

        clinet = APIClient()
        respond = clinet.post('/store/collections/',{'title':'a'})

        assert respond.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_if_user_is_authenticate_return_403(self):

        clinet = APIClient()
        clinet.force_authenticate(user={})
        respond = clinet.post('/store/collections/',{'title':'a'})

        assert respond.status_code == status.HTTP_403_FORBIDDEN

    def test_if_object_is_invalid_return_400(self):

        clinet = APIClient()
        clinet.force_authenticate(user=User(is_staff=True))
        respond = clinet.post('/store/collections/',{'title':''})

        assert respond.status_code == status.HTTP_400_BAD_REQUEST
        assert respond.data['title'] is not None

    def test_if_object_is_valid_return_201(self):

        clinet = APIClient()
        clinet.force_authenticate(user=User(is_staff=True))
        respond = clinet.post('/store/collections/',{'title':'love'})

        assert respond.status_code == status.HTTP_201_CREATED
        assert respond.data['id'] > 0

@pytest.mark.django_db
class TestRetriveCollection:
    def test_if_collection_exist(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        collection = baker.make(Collection)

        response = client.get(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'product_count': 0
        }
    
    def test_if_collection_not_exist(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))
        collection = baker.make(Collection)

        response = client.get(f'/store/collections/{collection.id+1}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
class TestUpdateCollection:
    def test_if_auth_user_can_modify_collection_return_403(self):
        client = APIClient()
        client.force_authenticate(user={})

        collection = baker.make(Collection)
        response = client.patch(f'/store/collections/{collection.id}/',{'title':'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_admin_user_can_modify_collection_return_200(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        title = 'love'
        collection = baker.make(Collection)
        response = client.patch(f'/store/collections/{collection.id}/',{'title':title})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == title


    

@pytest.mark.django_db
class TestDeleteCollection:
    def test_if_auth_user_can_delete_collection_return_403(self):
        client = APIClient()
        client.force_authenticate(user=User())

        collection = baker.make(Collection)
        response = client.delete(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_collection_can_be_deleted(self):
        client = APIClient()
        client.force_authenticate(user=User(is_staff=True))

        collection = baker.make(Collection)
        product = baker.make(Product,collection=collection)

        response = client.delete(f'/store/collections/{collection.id}/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN