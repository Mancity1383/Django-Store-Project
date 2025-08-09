from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()
router.register('products',ProductViewSet,basename='products')
router.register('collections',CollectionViewSet)

product_nested = routers.NestedDefaultRouter(router, 'products',lookup='product')
product_nested.register('reviews',ReviewViewSet,basename='product-reviews')

urlpatterns = router.urls + product_nested.urls