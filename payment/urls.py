from django.urls import path
from .views import *

app_name = 'payment'

urlpatterns = [
    path('pay/<int:order_id>/', PaymentView.as_view(), name='pay'),
    path('verify/', VerifyPaymentView.as_view(), name='verify'),
]