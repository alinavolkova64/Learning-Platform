import json
from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_authenticated:
            # Asynchronously add the user to the group
            await self.channel_layer.group_add(
                f'notifications_{user.id}',  # Group name is based on user ID
                self.channel_name,
            )
            # Accept the WebSocket connection
            await self.accept()

        # Close the WebSocket connection if the user is not authenticated
        else:
            await self.close()
        

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            # Remove the user from the notification group on disconnect
            await self.channel_layer.group_discard(
                f'notifications_{user.id}',
                self.channel_name 
            )

    async def receive(self, text_data):
        data = json.loads(text_data)  # Process the incoming message
        message = data['message']  # Extract the message

        # Send the message back to the WebSocket client
        await self.send(text_data=json.dumps({
            'message': message,
        }))
        #print(f"Receive method message: {message}")  # Debug log


    async def notify(self, event):
        print(f"Sending notification: {event['message']}")  # Log the event to check it's being sent
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'recipient': event['recipient'],
            'sender': event['sender'],
        }))
        #print(f"Notify method: {event['recipient']}")  # Debug log
