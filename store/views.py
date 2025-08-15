from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework import status
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter,OrderingFilter
from .filters import ProductFIlters
from .permission import IsAdminOrReadOnly,IsAdminOrAuth
from .models import *
from .serializers import *

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ProductFIlters
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
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
    permission_classes =[IsAdminOrReadOnly]
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
    
class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = Cart.objects.prefetch_related('items').all()
    serializer_class = CartSerializers

    def get_serializer_context(self):
        return {'request':self.request}

    
    # def destroy(self, request, *args, **kwargs):
    #     cart : Cart = self.get_object()
    #     if cart.items.count() > 0 :
    #         for item in cart.items.all():
    #             item.delete()
    #     self.perform_destroy(cart)
    #     return Response({'deleted':'The Cart got deleted'},status=status.HTTP_204_NO_CONTENT)
    
class CartItemsViewSet(ModelViewSet):
    http_method_names = ['get','post','delete','patch','head','options']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializers
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializers
        return GetCartItemsSerializers

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs['cart_pk'])
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk'],'request':self.request}
    

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializers
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        return {'user_id':self.request.user.id}
    
    @action(detail=False,methods=['GET','PUT'],permission_classes = [IsAuthenticated])
    def me(self,request):
        customer,created = Customer.objects.get_or_create(user_id=request.user.id)
        if self.request.method == 'GET':
            serializer = CustomerSerializers(customer)
            return Response(serializer.data)
        if self.request.method == 'PUT':
            serializer = CustomerSerializers(customer,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    http_method_names = ['get','post','delete','patch','head','options']
    pagination_class=PageNumberPagination

    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()
        
        return Order.objects.select_related('customer__user','customer').prefetch_related('items','items__product').filter(customer__user_id=self.request.user.id)
    
    def create(self, request, *args, **kwargs):
        serializers = POSTOrdersSerializers(context={'user_id':self.request.user.id,'request':self.request},data=request.data)
        serializers.is_valid(raise_exception=True)
        order = serializers.save()
        return Response(GETOrdersSerializers(order).data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return POSTOrdersSerializers
        return GETOrdersSerializers
    
    
