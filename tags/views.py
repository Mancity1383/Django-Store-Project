from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import CustomePermission
from .serializers import *
from .models import *
# Create your views here.

class TagViewSet(ModelViewSet):
    serializer_class = TagSerilizers
    filter_backends =[DjangoFilterBackend]
    filterset_fields = ['title']
    # permission_classes = [IsAdminUser]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        query = Tag.objects.prefetch_related('items','items__content_object').annotate(tagged_item_count=Count('items')).all()
        if product_id is not None:
            query = query.filter(items__object_id=product_id)
        return query

    def get_serializer_context(self):
        return {'request':self.request}
    
class TaggedItemViewSet(ModelViewSet):
    serializer_class = TaggedItemSerilizers
    # permission_classes = [CustomePermission]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return TaggedItem.objects.select_related('tag').prefetch_related('content_object').filter(tag_id=self.kwargs['tag_pk'])
    def get_serializer_context(self):
        return {'tag_id':self.kwargs['tag_pk'],'request':self.request}