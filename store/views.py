from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from .models import Product,Collection,OrderItem,Review
from .filters import ProductFIlters
from .serializers import ProductSerializers,CollectionSerializers,ReviewSerializers


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ProductFIlters
    pagination_class = PageNumberPagination
    search_fields = ['title','description']
    ordering_fields = ['id','title','price']

    def get_serializer_context(self):
        return {'request':self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error: There are some orderitems for this product'},status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(self.get_object())
        return Response({'deleted':'The product got deleted'},status=status.HTTP_204_NO_CONTENT)
        

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count = Count('products'))
    serializer_class = CollectionSerializers
    filter_backends = [OrderingFilter]
    ordering_fields = ['product_count']

    def get_serializer_context(self):
        return {'request':self.request}
    
    def destroy(self, request, *args, **kwargs):
        collection = self.get_object()
        if collection.products.count() > 0:
            return Response({'error: There are some products for this collection'},status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(collection)
        return Response({'deleted':'The collection got deleted'},status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializers
    filter_backends = [SearchFilter]
    search_fields = ['name','description']

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk'],'request':self.request}