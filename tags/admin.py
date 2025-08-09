from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(TaggedItem)
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ['title']