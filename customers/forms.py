from django import forms
from .models import Customer, Measurement


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'full_name', 'phone', 'email', 'address',
            'source', 'notes',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = [
            'customer', 'order', 'chest_circumference', 'waist_circumference',
            'hip_circumference', 'shoulder_width', 'sleeve_length',
            'arm_circumference', 'neck_circumference', 'garment_length',
            'skirt_trouser_length', 'notes',
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.Select(attrs={'class': 'form-select'}),
            'chest_circumference': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'cm'}),
            'waist_circumference': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'cm'}),
            'hip_circumference': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'cm'}),
            'shoulder_width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'cm'}),
            'sleeve_length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'cm'}),
            'arm_circumference': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'cm'}),
            'neck_circumference': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'cm'}),
            'garment_length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'cm'}),
            'skirt_trouser_length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'cm'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
