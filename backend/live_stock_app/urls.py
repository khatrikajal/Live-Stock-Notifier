from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('select_stock/', views.select_symbols, name='select_symbols'),
    path('stock_data/', views.fetch_stock_data, name='stock_data'),
 
]
