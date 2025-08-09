from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.html import format_html,urlencode
from django.urls import reverse
from django.db.models import Count
from tags.models import Tag,TaggedItem
from . import models
from .forms import OrderItemInlineFormset
# Register your models here.

class PriceFilter(admin.SimpleListFilter):
    title = 'Price'
    parameter_name = 'price'

    def lookups(self, request, model_admin):
        return [
            ('<10','Low Price'),
            ('10-30','Middle Price'),
            ('>30','High Price')
        ]
    
    def queryset(self, request, queryset):
        if self.value() == '<10':
            return queryset.filter(price__lte = 10)
        elif self.value() == '10-30':
            return queryset.filter(price__range=(10.01,30))
        elif self.value() == '>30':
            return queryset.filter(price__gte = 30) 

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','product_count']
    search_fields = ['title']
    @admin.display(ordering='product_count')
    def product_count(self,collection):
        url = reverse('admin:store_product_changelist') + '?' + urlencode({'collection_id':collection.id})
        return format_html(f'<a href ="{url}">{collection.product_count}</a>')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(product_count = Count('product'))

class TaggedInLine(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [TaggedInLine]
    autocomplete_fields = ['collection']
    prepopulated_fields = {
    'slug': ('title',)
    }
    actions = ['clear_inventory']
    list_display = ['title','collection__title','price','inventory_status']
    list_editable = ['price']
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title__istartswith']
    list_filter = ['collection',PriceFilter]

    @admin.display(ordering='inventory')
    def inventory_status(self,product : models.Product):
        if product.inventory < 10 :
            return 'Low'
        return 'OK'
    
    @admin.action(description='Clear Inventory')
    def clear_inventory(self,request,queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(request,f'{update_count} product updated inventory to 0.')
        
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["customer_full_name",'membership']
    list_editable = ["membership"]
    ordering = ['first_name','last_name']
    list_per_page = 10
    search_fields = ['customer_full_name']

    @admin.display(description="Full_Name")
    def customer_full_name(self,obj):
        return f"{obj.first_name} {obj.last_name}".title()
    
class OrderItemInLine(admin.TabularInline):
    formset = OrderItemInlineFormset
    autocomplete_fields = ['product']
    model = models.OrderItem
    extra = 1


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    list_display = ['id','customer_name','placed_at','payment_status']
    ordering = ['id']
    list_editable = ['payment_status']
    list_select_related = ['customer']
    list_per_page = 10
    inlines = [OrderItemInLine]

    @admin.display()
    def customer_name(self,order):
        # url = reverse('admin:store_customer_change', args=[order.customer.pk])
        url = reverse('admin:store_customer_changelist') + '?' +  urlencode({'id': order.customer.pk}) 
        return format_html(f"<a href='{url}'>{order.customer}</a>")