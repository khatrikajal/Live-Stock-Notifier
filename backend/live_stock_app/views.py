from django.shortcuts import render
import finnhub
from django.conf import settings



# Initialize Finnhub client with API key from settings
finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)


def home(request):
    return render(request, 'base.html')

def fetch_stock_data(request):
    # Define the country or exchange where you want to fetch symbols (example: 'US' for United States)
    country = 'US'
    
    # Fetch stock symbols from Finnhub
    try:
        stock_symbols = finnhub_client.stock_symbols(country)
        print("Stock symbols for country:", country)
        print(stock_symbols.symbol)
        context = {
            'stock_symbols': stock_symbols
        }
    except Exception as e:
        print(f"Error fetching stock symbols: {e}")
        stock_symbols = {'error': str(e)}

    # Return the fetched stock data as JSON response
    return render(request, 'stock_data.html', context)
