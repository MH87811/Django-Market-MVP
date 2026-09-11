from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from products.views import BaseVendorView


# Create your views here.

class TestNotificationView(BaseVendorView, View):
    def get(self, request, *args, **kwargs):
        channel_layer = get_channel_layer()
        group_name = f'seller_{request.user.id}'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'order_notification',
                'data': {
                    'message': 'test notifications',
                }
            }
        )

        return JsonResponse({
            'message': 'sent'
        })
