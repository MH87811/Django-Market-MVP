from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from notifications.models import Notification


@shared_task
def send_notification(notification_id):
    notification = Notification.objects.get(id=notification_id)
    channel_layer = get_channel_layer()
    group_name = f'seller_{notification.recipient_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification.message',
            'data': {
                'id': notification.id,
                'type': notification.type,
                'title': notification.title,
                'message': notification.message,
                'order_id': notification.order_id,
                'created_at': notification.created_at.isoformat(),
            }
        }
    )