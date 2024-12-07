import json
from channels.generic.websocket import AsyncWebsocketConsumer # type: ignore
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async
from django_celery_beat.models import PeriodicTask, IntervalSchedule # type: ignore
from finnhub import Client as FinnhubClient # type: ignore
from django.conf import settings
from .models import StockDetail


class StockConsumer(AsyncWebsocketConsumer):
    finnhub_client = FinnhubClient(api_key=settings.FINNHUB_API_KEY)

    @sync_to_async
    def add_to_celery_beat(self, stockpicker):
        task = PeriodicTask.objects.filter(name="every-10-seconds").first()
        if task:
            args = json.loads(task.args)[0]
            for stock in stockpicker:
                if stock not in args:
                    args.append(stock)
            task.args = json.dumps([args])
            task.save()
        else:
            schedule, _ = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
            PeriodicTask.objects.create(
                interval=schedule,
                name='every-10-seconds',
                task="live_stock_app.tasks.update_stock",
                args=json.dumps([stockpicker])
            )

    @sync_to_async
    def add_to_stock_detail(self, stockpicker):
        user = self.scope["user"]
        for stock in stockpicker:
            stock_detail, _ = StockDetail.objects.get_or_create(stock=stock)
            stock_detail.user.add(user)

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'stock_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Parse query_string
        query_params = parse_qs(self.scope["query_string"].decode())
        stockpicker = query_params.get('stockpicker', [])

        # Add to celery beat and stock details
        await self.add_to_celery_beat(stockpicker)
        await self.add_to_stock_detail(stockpicker)

        await self.accept()

    @sync_to_async
    def cleanup_user_stocks(self):
        user = self.scope["user"]
        user_stocks = StockDetail.objects.filter(user=user)
        task = PeriodicTask.objects.filter(name="every-10-seconds").first()
        args = json.loads(task.args)[0] if task else []

        for stock in user_stocks:
            stock.user.remove(user)
            if stock.user.count() == 0:
                args.remove(stock.stock)
                stock.delete()

        if task:
            if not args:
                task.delete()
            else:
                task.args = json.dumps([args])
                task.save()

    async def disconnect(self, close_code):
        await self.cleanup_user_stocks()

        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @sync_to_async
    def get_user_stocks(self):
        user = self.scope["user"]
        return list(user.stockdetail_set.values_list('stock', flat=True))

    async def send_stock_update(self, event):
        message = event['message']
        user_stocks = await self.get_user_stocks()

        # Filter stock data for the user
        filtered_data = {stock: data for stock, data in message.items() if stock in user_stocks}

        # Send filtered data to WebSocket
        await self.send(text_data=json.dumps(filtered_data))
