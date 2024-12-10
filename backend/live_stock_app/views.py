from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from finnhub import Client as FinnhubClient  # type: ignore
from django.conf import settings
from django.http import HttpResponse
from .models import User, StockDetail

# Initialize Finnhub client
finnhub_client = FinnhubClient(api_key=settings.FINNHUB_API_KEY)

# Home Page
def home(request):
    return render(request, 'home.html')

# Register User
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists.")
                return redirect('register')

            # Save User data
            user = form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('user_login')
        else:
            messages.error(request, "There was an error with your registration. Please try again.")
            print(f"Registering user error: {form.errors}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

# Login User
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            # Addition Login for superuser
            if user.is_superuser:
                messages.success(request, "You are now logged in as a superuser.")
                return redirect('dashboard')
            else:
                messages.success(request, "You are now logged in.")
                return redirect('select_symbols')
        else:
            messages.error(request, "Invalid Details. Please check your credentials.")
    else:
        form = AuthenticationForm()

    return render(request, 'user_login.html', {'form': form})

# Profile Update
def profile_update(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('home')
        else:
            messages.error(request, "There was an error updating your profile. Please try again.")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'profile_update.html', {'form': form})

# Logout User
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

# Stock Picker (Synchronous)
@login_required(login_url='/login')
def stock_picker(request):
    country = 'US'
    context = {}
    user = request.user

    try:
        # Fetch the list of available symbols
        symbols = finnhub_client.stock_symbols(country)

        # Get symbols already selected by the user
        user_stocks = StockDetail.objects.filter(users=user).values_list('stock', flat=True)

        # Prepare the list of available symbols excluding already selected ones
        stock_symbols = [
            {
                'symbol': symbol['symbol'],
                'description': symbol['description'],
            }
            for symbol in symbols if symbol['symbol'] not in user_stocks
        ]

        context['stock_symbols'] = stock_symbols

        # Handle stock selection
        if request.method == 'POST':
            # Get selected stocks
            selected_symbols = request.POST.getlist('stockpicker')

            # Save selected stocks in the database
            for symbol in selected_symbols:
                if not StockDetail.objects.filter(users=user, stock=symbol).exists():
                    StockDetail.objects.create(users=user, stock=symbol)

            return redirect('stock_data')

    except Exception as e:
        context['error'] = f'Error fetching stock symbols data: {e}'

    return render(request, 'select_symbols.html', context)

# Stock Tracker (Synchronous)
@login_required(login_url='/login')
def stock_tracker(request):
    user = request.user
    data = {}

    try:
        # Fetch the stocks selected by the user from the database
        user_stocks = StockDetail.objects.filter(users=user).values_list('stock', flat=True)

        if not user_stocks:
            return render(request, 'stock_data.html', {
                'data': data,
                'selected_stocks': "No stocks selected.",
            })

        # Fetch data for each stock
        for stock in user_stocks:
            try:
                stock_data = finnhub_client.quote(stock)

                if not stock_data:  # Handle empty response
                    data[stock] = {'error': "No data returned from API."}
                    continue

                price = stock_data.get('c', 0)  # Current price
                prev_close = stock_data.get('pc', 0)  # Previous close
                change = round(price - prev_close, 4)  # Calculate the change
                high = stock_data.get('h', 0)  # High price
                low = stock_data.get('l', 0)  # Low price
                down_percentage = stock_data.get('dp', 0)  # Down percentage

                # Determine change class for styling (positive: green, negative: red)
                change_class = 'text-success' if change > 0 else 'text-danger' if change < 0 else 'text-secondary'

                # Add stock data to dictionary
                data[stock] = {
                    'price': price,
                    'prev_close': prev_close,
                    'open': stock_data.get('o', 0),
                    'change': change,
                    'change_class': change_class,
                    'high': high,
                    'low': low,
                    'down_percentage': down_percentage,
                }
            except Exception as e:
                # Log error and skip the current stock
                data[stock] = {'error': f"Error fetching data for {stock}: {e}"}

    except Exception as e:
        return HttpResponse(f"Error fetching user stocks: {e}")

    # Render the stock data page
    return render(request, 'stock_data.html', {
        'data': data,
        'selected_stocks': ", ".join(user_stocks)
    })
