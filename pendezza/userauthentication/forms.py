from django import forms
from django.contrib.auth.forms import UserCreationForm

from userauthentication.models import User, Profile

class UserRegisterForm(UserCreationForm):
  full_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Enter Full name", 'class': "custom_class"}))
  username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Enter username"}))
  email = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Enter email"}))
  password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))
  password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Confirm Password"}))
  class Meta:
    model = User
    fields = ['full_name', 'username', 'email', 'phone', 'password1', 'password2']


    