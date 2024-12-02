import finnhub
from celery import shared_task
from django.conf import settings  # Import settings to access the environment variables

# Initialize the Finnhub client with the API key from settings
finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)


@shared_task
def update_stock(stock_symbols):
    # Task logic here
    pass
    
@shared_task
def fetch_stock_data(ticker):
    """
    Fetch stock data for a given ticker using Finnhub.
    """
    try:
        # Fetch stock data for the given ticker (e.g., 'AAPL')
        stock_data = finnhub_client.quote(ticker)
        
        # Print or process the stock data (for example, save it to a database)
        print(stock_data)
        
        # Here, you could save the stock data to your models or perform other actions
        # For example, you could save it to a Stock model like so:
        # Stock.objects.create(ticker=ticker, data=stock_data)
        
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {str(e)}")