from django.shortcuts import render
from django.http import JsonResponse
import finnhub
from django.conf import settings
from django.http import HttpResponse

# Initialize Finnhub client with API key from settings
finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)


def home(request):
    return HttpResponse("<h1>Welcome to the Live Stock Notifier</h1>")

def fetch_stock_data(request):
    # Define the country or exchange where you want to fetch symbols (example: 'US' for United States)
    country = 'US'
    
    # Fetch stock symbols from Finnhub
    try:
        stock_symbols = finnhub_client.stock_symbols(country)
        print("Stock symbols for country:", country)
        print(stock_symbols)
    except Exception as e:
        print(f"Error fetching stock symbols: {e}")
        stock_symbols = {'error': str(e)}

    # Return the fetched stock data as JSON response
    return JsonResponse(stock_symbols, safe=False)
