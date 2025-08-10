from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()
router.register('products',ProductViewSet,basename='products')
router.register('collections',CollectionViewSet)
router.register('carts',CartViewSet)
router.register('customers',CustmerViewSet)

product_nested = routers.NestedDefaultRouter(router, 'products',lookup='product')
product_nested.register('reviews',ReviewViewSet,basename='product-reviews')

cart_nested = routers.NestedSimpleRouter(router,'carts',lookup = 'cart')
cart_nested.register('items',CartItemsViewSet,basename='cart-items')

urlpatterns = router.urls + product_nested.urls + cart_nested.urls