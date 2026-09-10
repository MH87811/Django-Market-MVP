from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import *
from django.db import transaction
from products.models import ProductVariant
from .forms import *
from .models import *

# Create your views here.

# class CartListView(ListView):
#
    
class CartDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        carts = Cart.objects.prefetch_related('cart_items').filter(
            user=request.user,
        ).select_related('seller')
        ctx = {
            'carts': carts,
        }
        return render(request, 'shopcarts/detail.html', ctx)

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, variant_id, *args, **kwargs):
        variant = get_object_or_404(ProductVariant, pk=variant_id)
        form = AddToCartForm(request.POST)

        if not form.is_valid():
            messages.error(request, 'invalid quantity')
            print('invalid quantity')
            return redirect('products:detail', slug=variant.product.slug)

        if not variant.product.is_available:
            messages.error(request, 'product unavailable')
            print('product unavailable')
            return redirect('products:detail', slug=variant.product.slug)

        quantity = form.cleaned_data['quantity']

        if variant.stock < quantity:
            messages.error(request, 'not enough stock')
            print('not enough stock')
            return redirect('products:detail', slug=variant.product.slug)

        cart, _ = Cart.objects.get_or_create(user=request.user, seller=variant.product.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                'quantity': quantity
            }
        )

        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > variant.stock:
                messages.error(request, 'not enough stock')
                print('not enough stock')
                return redirect('products:detail', slug=variant.product.slug)

            cart_item.quantity = new_quantity
            cart_item.save(
                update_fields=[
                    'quantity',
                    'updated_at',
                ]
            )

        messages.success(request, 'Product added to cart.')
        return redirect('shopcarts:detail')

class UpdateCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id, *args, **kwargs):
        cart_item = get_object_or_404(
            CartItem.objects.select_related('variant'),
            pk=item_id,
            cart__user=request.user
        )

        form = UpdateCartItemForm(request.POST)
        if not form.is_valid():
            messages.error(
                request,
                'Invalid quantity.',
            )
            print('Invalid quantity.')
            return redirect('shopcarts:detail')

        quantity = form.cleaned_data['quantity']
        if quantity > cart_item.variant.stock:
            messages.error(
                request,
                'Not enough stock available.',
            )
            print('Not enough stock available.')
            return redirect('shopcarts:detail')

        cart_item.quantity = quantity
        cart_item.save(
            update_fields=[
                'quantity',
                'updated_at',
            ]
        )

        messages.success(request, 'Cart updated successfully.')
        return redirect('shopcarts:detail')


class RemoveCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id, *args, **kwargs):
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)

        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
        return redirect('shopcarts:detail')


class ClearCartView(LoginRequiredMixin, View):
    def post(self, request, cart_id, *args, **kwargs):
        cart = get_object_or_404(Cart, id=cart_id, user=request.user)

        cart.cart_items.all().delete()
        messages.success(request, 'Cart cleared successfully.')

        return redirect('shopcarts:detail')