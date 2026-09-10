from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import constraints

# Create your models here.

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='carts')
    seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sell_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return sum(item.total_price for item in self.cart_items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.cart_items.all())

    def __str__(self):
        return f'{self.user} cart'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'seller'],
                name='unique_user_seller',
            )
        ]

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'variant'],
                name='unique_cart_variant'
            )
        ]

    @property
    def unit_price(self):
        return self.variant.get_final_price()

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f'{self.cart} - {self.variant}: {self.quantity}'