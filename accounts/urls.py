from .views import *
from django.urls import path

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('edit_profile', ProfileEditView.as_view(), name='edit_profile'),
    path('delete_user/', UserDeleteView.as_view(), name='delete_user'),
]
