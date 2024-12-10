from celery import shared_task
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer # type: ignore
from .models import StockDetail
from finnhub import Client as FinnhubClient # type: ignore

# Initialize Finnhub client
finnhub_client = FinnhubClient(api_key=settings.FINNHUB_API_KEY)


@shared_task
def fetch_stock_data():
    """
    Periodically fetch stock data from the Finnhub API and update the StockDetail model.
    """
    stock_details = StockDetail.objects.all()

    for stock_detail in stock_details:
        symbol = stock_detail.stock

        try:
            # Fetch stock data from Finnhub API
            stock_data = finnhub_client.quote(symbol)
            if stock_data:
                price = stock_data.get('c', 0)  # Current price
                prev_close = stock_data.get('pc', 0)  # Previous close
                change = round(price - prev_close, 4)  # Calculate the change
                high = stock_data.get('h', 0)  # High price
                low = stock_data.get('l', 0)  # Low price

                # Update the database
                stock_detail.price = price
                stock_detail.prev_close = prev_close
                stock_detail.change = change
                stock_detail.high = high
                stock_detail.low = low
                stock_detail.save()

                # Notify the users via WebSocket
                send_stock_data_to_websocket(stock_detail.users, stock_detail)

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    return "Stock data updated."


def send_stock_data_to_websocket(users, stock_detail):
    """
    Send stock data to WebSocket for all users tracking the stock.
    """
    channel_layer = get_channel_layer()

    stock_data = {
        'symbol': stock_detail.stock,
        'price': stock_detail.price,
        'change': stock_detail.change,
        'prev_close': stock_detail.prev_close,
        'high': stock_detail.high,
        'low': stock_detail.low,
    }

    for user in users.all():
        group_name = f"stock_{user.id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'stock_data',
                'data': stock_data
            }
        )
