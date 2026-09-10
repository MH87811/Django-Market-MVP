from .views import *
from django.urls import path

app_name = 'shopcarts'

urlpatterns = [
    path('', CartDetailView.as_view(), name='detail'),
    path('add/<int:variant_id>/', AddToCartView.as_view(), name='add'),
    path('item/<int:item_id>/update/', UpdateCartItemView.as_view(), name='update'),
    path('item/<int:item_id>/remove/', RemoveCartItemView.as_view(), name='remove'),
    path('clear/<int:cart_id>', ClearCartView.as_view(), name='clear'),
]