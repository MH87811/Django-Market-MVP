from django.urls import path
from .views import *

app_name = 'panels'

urlpatterns = [
    path('dashboard/', BuyerDashboardView.as_view(), name='buyer-dash'),
    path('panel/', VendorDashboardView.as_view(), name='vendor-dash'),
]