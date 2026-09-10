from django import forms
from .models import *

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)

class UpdateCartItemForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)