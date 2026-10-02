from django.views import View
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from utils.tasks import send_notification
from utils.vendor_view import BaseVendorView


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

class TestCeleryNotificationView(BaseVendorView, View):
    def get(self, request, *args, **kwargs):
        task = send_notification.delay(
            request.user.id,
            1,
            'new_order',
            'New order',
            'a new order registered'
        )
        return JsonResponse({
            'message': 'sent',
            'task_id': task.id,
        })