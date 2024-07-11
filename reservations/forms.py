from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, House, Order, Review

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'phonenumber', 'address']

class LoginForm(AuthenticationForm):
    pass

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['name', 'image', 'city', 'number_of_rooms', 'area', 'number_of_parkings', 'capacity', 'price_per_day', 'pool', 'oven']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['arrive_date', 'exit_date', 'count_of_passengers']
        widgets = {
            'arrive_date': forms.DateInput(attrs={'type': 'date'}),
            'exit_date': forms.DateInput(attrs={'type': 'date'}),
        }

class RoleChangeRequestForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []  # No fields, just a button to request role change

class UserInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phonenumber', 'address']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']