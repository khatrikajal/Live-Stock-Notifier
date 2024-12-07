from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from finnhub import Client as FinnhubClient # type: ignore
from django.conf import settings
from django.http import HttpResponse
from .models import User

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

# Stock Picker
@login_required(login_url='/login')
async def stock_picker(request):
    stock_list = finnhub_client.stock_symbols('US')  # Example: Fetch US stocks
    return render(request, 'select_symbols.html', {'stockpicker': stock_list})

# Stock Tracker
@login_required(login_url='/login')
async def stock_tracker(request):
    stockpicker = request.GET.getlist('stockpicker')
    selected_stocks = ", ".join(stockpicker)

    data = {}
    for stock in stockpicker:
        try:
            stock_data = finnhub_client.quote(stock)
            price = stock_data.get('c', 0)  # Current price
            prev_close = stock_data.get('pc', 0)  # Previous close
            change = round(price - prev_close, 4)  # Calculate the change
            change_class = 'green' if change > 0 else 'red' if change < 0 else ''  # Set class for color
            data[stock] = {
                'price': price,
                'prev_close': prev_close,
                'open': stock_data.get('o', 0),
                'change': change,
                'change_class': change_class,
                'market_cap': stock_data.get('marketCap', 0),
                'volume': stock_data.get('v', 0)
            }
        except Exception as e:
            return HttpResponse(f"Error fetching data for {stock}: {e}")

    return render(request, 'stock_data.html', {
        'data': data,
        'selected_stocks': selected_stocks
    })
