
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Product

class OrderItemInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()

        product_quantities = {}

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data.get('DELETE', False):
                continue

            product = form.cleaned_data.get('product')
            qty = form.cleaned_data.get('quantity') or 0

            if product:
                product_quantities[product.pk] = product_quantities.get(product.pk, 0) + qty

        for product_pk, total_qty in product_quantities.items():
            product = Product.objects.get(pk=product_pk)
            if total_qty > product.inventory:
                raise ValidationError(
                    f'Not enough inventory for "{product.title}". Available: {product.inventory}, requested: {total_qty}.'
                )
