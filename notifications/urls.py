from django.urls import path
from .views import *

app_name = 'notifications'

urlpatterns = [
    path('test', TestNotificationView.as_view(), name='test')
]