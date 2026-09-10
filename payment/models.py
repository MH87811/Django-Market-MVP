from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class Payment(models.Model):
    order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='payments')
    amount = models.PositiveIntegerField()
    authority = models.CharField(max_length=128, null=True, blank=True, unique=True)
    ref_id = models.CharField(max_length=128, null=True, blank=True, unique=True)

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    ALLOWED_TRANSITIONS = {
        StatusChoices.PENDING: {StatusChoices.SUCCESS, StatusChoices.FAILED},
        StatusChoices.SUCCESS: set(),
        StatusChoices.FAILED: set(),
    }

    status = models.CharField(max_length=10, choices=StatusChoices, default=StatusChoices.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def change_status(self, new_status):
        if not new_status in self.ALLOWED_TRANSITIONS[self.status]:
            raise ValueError('invalid status transition')
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])