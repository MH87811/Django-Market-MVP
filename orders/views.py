from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from .forms import *
from .models import *
from shopcarts.models import Cart
from products.models import ProductVariant

# Create your views here.

class CreateOrderView(LoginRequiredMixin, View):
    def post(self, request, cart_id, *args, **kwargs):
        cart = get_object_or_404(Cart, id=cart_id, user=request.user)
        cart_items = list(cart.cart_items.select_related('variant', 'variant__product'))

        if not cart_items:
            raise ValueError('Cart is empty')

        variant_ids = [
            item.variant_id
            for item in cart_items
        ]

        with transaction.atomic():
            variants = {
                variant.id: variant
                for variant in ProductVariant.objects
                .select_for_update()
                .select_related('product')
                .filter(id__in=variant_ids)
            }
            order = Order.objects.create(user=cart.user, total_price=cart.get_total_price())
            for item in cart_items:
                variant = variants.get(item.variant_id)

                if not variant.product.is_available:
                    raise ValueError(f'{variant.product} not available')

                if item.quantity > variant.stock:
                    raise ValueError(f'{variant}: not enough stock')

                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    quantity=item.quantity,
                    unit_price=variant.get_final_price(),
                )
            cart_items.delete()
            return redirect('payment')