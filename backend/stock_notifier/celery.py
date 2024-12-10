# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from datetime import timedelta
from django.conf import settings

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_notifier.settings')

# Initialize the Celery application
app = Celery('stock_notifier')

# Celery configuration settings
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Kolkata')

# Load configuration from Django settings
app.config_from_object(settings, namespace='CELERY')

# Celery beat schedule to run the task every 10 seconds
app.conf.beat_schedule = {
    'fetch_stock_periodically': {
        'task': 'live_stock_app.tasks.fetch_stock_data',  # Your task to fetch stock data
        'schedule': timedelta(seconds=10),  # Fetch stock data every 10 seconds
        
    },
}

# Autodiscover tasks in registered apps
app.autodiscover_tasks(['live_stock_app'])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
