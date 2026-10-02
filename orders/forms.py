from django import forms
from django.db import transaction
from products.models import ProductVariant
from .models import *
from utils.shipping import ShippingProvider


class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('address', 'zip_code')

    def __init__(self, *args, **kwargs):
        self.cart = kwargs.pop('cart')

        super().__init__(*args, **kwargs)
        self.user_address = self.cart.user.profile.address
        self.user_zip_code = self.cart.user.profile.zip_code
        self.cart_items = list(
            self.cart.cart_items.select_related(
                'variant',
                'variant__product',
            )
        )

    def clean(self):
        cleaned_data = super().clean()

        if not self.cart_items:
            raise forms.ValidationError('The cart is empty.')

        address = cleaned_data.get('address') or self.user_address
        zip_code = cleaned_data.get('zip_code') or self.user_zip_code

        if not address:
            raise forms.ValidationError('Address not provided, please either fill the address field or complete your profile.')

        if not zip_code:
            raise forms.ValidationError('Zip code not provided, please either fill the zip code field or complete your profile.')

        cleaned_data['address'] = address
        cleaned_data['zip_code'] = zip_code

        return cleaned_data

    def save(self, commit=True):
        if not commit:
            raise ValueError('OrderCreationForm requires commit=True.')

        with transaction.atomic():
            cart_items = list(
                self.cart.cart_items.select_related(
                    'variant',
                    'variant__product',
                )
            )

            if not cart_items:
                raise forms.ValidationError('The cart is empty.')

            variant_ids = [item.variant_id for item in cart_items]

            variants = {
                variant.id: variant
                for variant in (
                    ProductVariant.objects
                    .select_for_update()
                    .select_related('product')
                    .filter(id__in=variant_ids)
                    .order_by('id')
                )
            }

            total_price = 0

            for item in cart_items:
                variant = variants.get(item.variant_id)
                if variant is None:
                    raise forms.ValidationError('A product variant no longer exists.')

                if not variant.product.is_available:
                    raise forms.ValidationError(f'{variant.product} is not available.')

                if item.quantity > variant.stock:
                    raise forms.ValidationError(f'{variant}: not enough stock.')

                total_price += (variant.get_final_price() * item.quantity)

            order = Order.objects.create(
                user=self.cart.user,
                seller=self.cart.seller,
                total_price=total_price,
                address=self.cleaned_data['address'],
                zip_code=self.cleaned_data['zip_code'],
            )

            for item in cart_items:
                variant = variants[item.variant_id]
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    quantity=item.quantity,
                    unit_price=variant.get_final_price(),
                )

            self.cart.cart_items.all().delete()

        return order

class ShipOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('tracking_code',)

    tracking_code = forms.RegexField(regex=r'^[0-9]{10}$', max_length=10)

    # def clean_tracking_code(self):
    #     provider = PostShippingProvider()
    #     tracking_code = self.cleaned_data['tracking_code']
    #     if not ShippingProvider.validate_tracking_code(tracking_code):
    #         raise forms.ValidationError('invalid tracking code')