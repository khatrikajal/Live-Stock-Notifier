from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('user_login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='logout'),
    path('select_symbols/', views.stock_picker, name = 'select_symbols'),
    path('stock_data/', views.stock_tracker, name = 'stock_data'),
 
]
