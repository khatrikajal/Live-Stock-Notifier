from celery import shared_task
from finnhub import Client as FinnhubClient # type: ignore
from django.conf import settings
from channels.layers import get_channel_layer # type: ignore
import asyncio

# Initialize Finnhub client
finnhub_client = FinnhubClient(api_key=settings.FINNHUB_API_KEY)

@shared_task
def update_stock(stockpicker):
    data = {}
    for stock in stockpicker:
        try:
            # Fetch stock data from Finnhub
            stock_data = finnhub_client.quote(stock)
            data[stock] = stock_data
        except Exception as e:
            print(f"Error fetching data for {stock}: {e}")

    # Send data to the WebSocket group
    channel_layer = get_channel_layer()
    asyncio.run(channel_layer.group_send("stock_track", {
        'type': 'send_stock_update',
        'message': data,
    }))
    return "Done"
