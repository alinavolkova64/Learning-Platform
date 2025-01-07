from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        
        # Loop over recipients since it's a Many-to-Many field
        for recipient in instance.recipient.all():  
            async_to_sync(channel_layer.group_send)(
                f'notifications_{recipient.id}', {  # Use each recipient's ID
                    "type": "notify",
                    "message": instance.message,
                    "sender": instance.sender.id,
                    "timestamp": instance.timestamp,
                    "recipient": recipient.id,
                }
            )