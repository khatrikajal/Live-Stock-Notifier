from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
import json

class StockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "stock_track"  # Group name for stock updates

        # Join the stock tracking group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the stock tracking group on disconnect
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Here you can handle messages like subscribing or unsubscribing to specific stock tickers
        # data = json.loads(text_data)
        # action = data.get('action')
        # ticker = data.get('ticker')

        # Example of subscribing to a stock ticker
        # if action == 'subscribe' and ticker:
        #     # Handle subscription logic (e.g., maintaining a list of tickers the client is interested in)
        #     pass

        # Example of unsubscribing from a stock ticker
        # elif action == 'unsubscribe' and ticker:
        #     # Handle unsubscription logic
        #     pass

        pass  # You can customize this as per your needs

    # Receive message from the Celery task
    async def send_stock_update(self, event):
        # Send the stock data received from the Celery task to WebSocket clients
        await self.send(text_data=json.dumps(event['message']))
