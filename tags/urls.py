from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()
router.register('tags',TagViewSet)

tag_nested = routers.NestedDefaultRouter(router,'tags',lookup='tag')
tag_nested.register('items',TaggedItemViewSet,basename='tag-items')

urlpatterns = router.urls + tag_nested.urls