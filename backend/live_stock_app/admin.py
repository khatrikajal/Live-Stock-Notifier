from django.contrib import admin
from .models import User, StockDetail

# Register the custom User model in the admin
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined', 'last_login', 'is_superuser')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'username', 'password1', 'password2')}),
    )
    


admin.site.register(User, UserAdmin)

# Register StockDetail model in admin
class StockDetailAdmin(admin.ModelAdmin):
    list_display = ('stock', 'users')
    search_fields = ('stock',)
    list_filter = ('users',)
    
admin.site.register(StockDetail, StockDetailAdmin)
