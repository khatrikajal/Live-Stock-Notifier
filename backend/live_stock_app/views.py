from django.shortcuts import render
import finnhub  # type: ignore
from django.conf import settings

# Initialize Finnhub client with API key from settings
finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)

def home(request):
    return render(request, 'base.html')

def select_symbols(request):
    country = 'US'
    context = {}
    try:
        # Fetch the list of available symbols
        symbols = finnhub_client.stock_symbols(country)
        stock_symbols = []

        for symbol in symbols:
            stock_symbols.append({
                'symbol': symbol['symbol'],
                'description': symbol['description']
            })  # Add both symbol and description to the list

        context['stock_symbols'] = stock_symbols  # Pass the list of dictionaries to the template

    except Exception as e:
        context['error'] = f"Error fetching stock Symbols data: {e}"

    return render(request, 'select_symbols.html', context)


def fetch_stock_data(request):
    country = 'US'
    context = {}

    try:
        stock_symbols = finnhub_client.stock_symbols(country)
        stock_data_with_prices = [] # Creating empty list

        # Fetch stock prices for each symbol
        for stock in stock_symbols:  # Limit for performance
            try:
                stock_price = finnhub_client.quote(stock['symbol'])
                
                # Add stock price details to the stock data dictionary
                stock_data = {
                    'symbol': stock['symbol'],
                    'currency': stock.get('currency', 'N/A'),
                    'description': stock.get('description', 'No Description'),
                    'type': stock.get('type', 'N/A'),
                    'c': stock_price['c'],  # Current price
                    'h': stock_price['h'],  # High price
                    'l': stock_price['l'],  # Low price
                    'dp': stock_price['dp'],  # Down percentage
                    'pc': stock_price['pc'],  # Previous close
                }
                stock_data_with_prices.append(stock_data)
            except Exception as e:
                print(f"Error fetching price for {stock['symbol']}: {e}")
        
        context['stock_symbols'] = stock_data_with_prices

    except Exception as e:
        context['error'] = f"Error fetching stock data: {e}"

    return render(request, 'stock_data.html', context)
