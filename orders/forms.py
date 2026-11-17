from django import forms
from .models import Order
from accounts.models import User


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer', 'designer', 'status', 'required_date', 'description',
            'total_amount', 'dp_amount', 'notes',
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'designer': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'required_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'dp_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only designer users can be assigned as order designer.
        self.fields['designer'].queryset = User.objects.filter(role__code='DESIGNER')
        self.fields['designer'].empty_label = 'Select designer (optional)'
