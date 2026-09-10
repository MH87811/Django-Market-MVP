from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from .models import *

User = get_user_model()

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Confirm Your Password')

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'is_vendor']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already in use')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already in use')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Phone number already in use')
        return phone

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        password2 = cleaned.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError('Passwords do not match')
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            password=self.cleaned_data['password'],
            is_vendor=self.cleaned_data['is_vendor']
        )
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, label='Username')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')

    def clean(self):
        cleaned = super().clean()
        user = authenticate(username=cleaned['username'], password=cleaned['password'])
        if not user:
            raise forms.ValidationError('Username or Password is incorrect')
        cleaned['user'] = user
        return cleaned

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'address', 'zip_code', 'image', 'bio', 'shop_name', 'shop_logo', 'shop_info')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        vendor_fields = ['shop_name', 'shop_logo', 'shop_info']
        if not self.user.is_vendor:
            for field in vendor_fields:
                self.fields.pop(field)