from market_CBV.celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market_CBV.settings')

app = Celery('market_CBV')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()