from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.views.generic import *
from django.urls import reverse_lazy
from .forms import *
from .models import Profile

# Create your views here.

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:edit_profile')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        login(self.request, user)
        return super().form_valid(form)

class Logout(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('accounts:login')

class ProfileView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/profile.html'
    model = Profile

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('accounts:profile')
    form_class = ProfileForm

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Your profile updated successfully!')
        return super().form_valid(form)

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'accounts/user_delete.html'
    success_url = reverse_lazy('accounts:register')

    def get_object(self):
        return User.objects.get(id=self.request.user.id)

    def delete(self, request, *args, **kwargs):
        logout(request)
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, 'your account deleted successfully')
        return redirect(self.success_url)