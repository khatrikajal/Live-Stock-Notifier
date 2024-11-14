from django.shortcuts import render
from yahoo_fin.stock_info import tickers_nifty50
from django.http import HttpResponse

def stockPicker(request):
    stock_picker = tickers_nifty50()
    print(stock_picker)  # This will print the stock list to the console
    return HttpResponse(stock_picker)  # Return the stock list in the HTTP response
