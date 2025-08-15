from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import *
from .models import *
# Create your views here.

class TagViewSet(ModelViewSet):
    queryset = Tag.objects.prefetch_related('items','items__content_object').all()
    serializer_class = TagSerilizers

    def get_serializer_context(self):
        return {'request':self.request}
    
class TaggedItemViewSet(ModelViewSet):
    serializer_class = TaggedItemSerilizers

    def get_queryset(self):
        return TaggedItem.objects.select_related('tag').prefetch_related('content_object').filter(tag_id=self.kwargs['tag_pk'])
    def get_serializer_context(self):
        return {'tag_id':self.kwargs['tag_pk'],'request':self.request}