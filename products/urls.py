from .views import *
from django.urls import path

app_name = 'products'

urlpatterns = [
    path('add/', AddProductView.as_view(), name='add'),
    path('list/', ProductListView.as_view(), name='list'),
    path('detail/<slug:slug>', ProductDetailView.as_view(), name='detail'),
    path('update/<slug:slug>', ProductUpdateView.as_view(), name='update'),
    path('delete/<slug:slug>', ProductDeleteView.as_view(), name='delete'),
    path('<slug:slug>/variant/add', AddVariantView.as_view(), name='add_variant'),
    path('<slug:slug>/variant/<int:id>/update', VariantUpdateView.as_view(), name='update_variant'),
    path('<slug:slug>/variant/<int:id>/delete', VariantDeleteView.as_view(), name='delete_variant'),
]