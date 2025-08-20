from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User, ROLE_CHOICES, Profile
from salon.models import Salon


class UserRegisterForm(UserCreationForm):
  full_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Enter Full name", 'class': "custom_class"}))
  username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Enter username"}))
  email = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Enter email"}))
  phone = forms.CharField( widget=forms.TextInput(attrs={"placeholder": "Enter phone number"}), max_length=20, required=True)
  role = forms.ChoiceField(choices=ROLE_CHOICES)
  password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))
  password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Confirm Password"}))
  class Meta:
      model = User
      fields = ['full_name', 'username', 'email', 'phone', 'role', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    # Common fields
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter address'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Tell us about yourself'}), required=False)
    
    # Salon owner fields
    salon_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Salon name'}),
        required=False
    )
    salon_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Salon email'}),
        required=False
    )
    salon_mobile = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Salon phone number'}),
        required=False
    )
    salon_description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Describe your salon'}),
        required=False
    )
    salon_image = forms.ImageField(required=False)
    
    # Staff fields
    salon = forms.ModelChoiceField(
        queryset=Salon.objects.all(),
        required=False
    )
    specialization = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Your specializations'}),
        required=False
    )
    hire_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = [
            'country', 'state', 'city', 'address', 
            'identity_type', 'identity_image', 'linkedin', 'twitter',
            'salon_name', 'salon_email', 'salon_mobile', 'salon_description', 'salon_image',
            'salon', 'specialization', 'hire_date', 'bio', 'profile_pic'
        ]

    def __init__(self, *args, **kwargs):
        role = kwargs.pop('role', None)
        super().__init__(*args, **kwargs)
        
        # Show/hide fields based on role
        if role == 'owner':
            for field in ['salon', 'specialization', 'hire_date']:
                self.fields[field].widget = forms.HiddenInput()
        elif role == 'staff':
            for field in ['salon_name', 'salon_email', 'salon_mobile', 'salon_description', 'salon_image']:
                self.fields[field].widget = forms.HiddenInput()