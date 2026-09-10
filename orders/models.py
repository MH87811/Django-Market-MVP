from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders')
    seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sell_carts')
    total_price = models.PositiveIntegerField()
    tracking_code = models.CharField(max_length=24, unique=True, blank=True, null=True)

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        CANCELLED = 'cancelled', 'Cancelled'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'

    ALLOWED_TRANSITIONS = {
        StatusChoices.PENDING: {StatusChoices.PAID, StatusChoices.CANCELLED},
        StatusChoices.CANCELLED: set(),
        StatusChoices.PAID: {StatusChoices.CANCELLED, StatusChoices.SHIPPED},
        StatusChoices.SHIPPED: {StatusChoices.DELIVERED},
        StatusChoices.DELIVERED: set(),
    }

    status = models.CharField(max_length=11 ,choices=StatusChoices, default=StatusChoices.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} order'

    def change_status(self, new_status):
        if new_status not in self.ALLOWED_TRANSITIONS[self.status]:
            raise ValueError('invalid transition')
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.PositiveIntegerField()

    def __str__(self):
        return f'order: {self.order} - {self.variant}: {self.quantity}'