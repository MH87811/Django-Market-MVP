from django.shortcuts import render
from django.views.generic import *

# Create your views here.

class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'core/index.html')

class DashboardView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'vendors/dashboard.html')
