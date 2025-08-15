from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
# Create your models here.

class TagItemMannager(models.Manager):
    def get_tags_for(self,object_type,objct_id):
        content_type = ContentType.objects.get_for_model(object_type)
        tagged_item = TaggedItem.objects.select_related('tag').filter(content_type=content_type,objct_id=objct_id)
        
        return tagged_item

class Tag(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class TaggedItem(models.Model):
    objects = TagItemMannager()
    tag = models.ForeignKey(Tag,on_delete=models.CASCADE,related_name='items')
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()