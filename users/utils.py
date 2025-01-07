from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_notification(notification):
    """
    Helper function to send WebSocket notifications to all recipients of a notification, 
    by explicitly calling the 'notify' method in consumers.py, delivering the notification data.
    """
    # Get the channel layer for WebSocket communication
    channel_layer = get_channel_layer()
    for recipient in notification.recipient.all():
        # Use group_send to send a message to the WebSocket group for each recipient
        async_to_sync(channel_layer.group_send)(
            f'notifications_{recipient.user.id}',
            {
                'type': 'notify',
                'message': notification.message,
                'recipient': recipient.id,
                'sender': notification.sender.id if notification.sender else None,
            }
        )
