import json
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
from .models import StockDetail


class StockConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.room_group_name = f"stock_{self.user.id}"

            # Join user's stock update group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Send initial stock data to WebSocket
            stock_data = await self.get_stock_data()
            await self.send_stock_data(stock_data)
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave the stock update group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle messages received from WebSocket, if needed
        pass

    async def stock_data(self, event):
        # Send updated stock data to WebSocket
        stock_data = event['data']
        await self.send(text_data=json.dumps(stock_data))

    async def get_stock_data(self):
        # Retrieve stocks associated with the user
        stock_details = StockDetail.objects.filter(users=self.user)
        stock_data = {}

        for stock in stock_details:
            stock_data[stock.stock] = {
                'symbol': stock.stock,
                'price': stock.price,
                'change': stock.change,
                'prev_close': stock.prev_close,
                'high': stock.high,
                'low': stock.low
            }

        return stock_data

    async def send_stock_data(self, stock_data):
        # Send stock data to WebSocket
        await self.send(text_data=json.dumps(stock_data))
