from django import forms
from .models import Review
from django.contrib.auth.forms import AuthenticationForm

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating', 'food_img']

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваш логін або пошта',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Ваш пароль',
    }))
