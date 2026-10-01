from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, related_name='notifications', null=True, blank=True)

    class TypeChoices(models.TextChoices):
        NEW_ORDER = 'new_order', 'New Order'
        ORDER_CANCELLED = 'order_cancelled', 'Order Cancelled'
        PAYMENT_RECEIVED = 'payment_received', 'Payment Received'
        ORDER_SHIPPED = 'order_shipped', 'Order Shipped'

    type = models.CharField(max_length=64, choices=TypeChoices, default=TypeChoices.NEW_ORDER)
    title = models.CharField(max_length=64)
    is_seen = models.BooleanField(default=False)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.recipient}: {self.order}'