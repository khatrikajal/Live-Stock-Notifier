from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('register/', views.register, name='register'),  # User registration
    path('login/', views.user_login, name='user_login'),  # User login
    path('logout/', views.user_logout, name='user_logout'),  # User logout
    path('profile-update/', views.profile_update, name='profile_update'),  # Profile update
    path('select-symbols/', views.stock_picker, name='select_symbols'),  # Stock picker page
    path('stock-data/', views.stock_tracker, name='stock_data'),  # Stock tracker page
]
