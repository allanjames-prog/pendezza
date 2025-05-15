from django import forms
from .models import SalonServices

class SalonServiceForm(forms.ModelForm):
    class Meta:
        model = SalonServices
        fields = [
            'name', 'description', 'base_price', 'women_price',
            'men_price', 'children_price', 'duration', 'category',
            'gender', 'is_featured', 'is_active', 'icon', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }