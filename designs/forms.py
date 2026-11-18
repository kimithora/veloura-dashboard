from django import forms
from .models import Design
from accounts.models import User


class DesignForm(forms.ModelForm):
    class Meta:
        model = Design
        fields = [
            'order', 'name', 'category', 'sketch', 'customer_reference',
            'fabric', 'color', 'style_description', 'designer', 'status',
            'estimated_cost', 'estimated_duration_days', 'notes',
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'sketch': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'customer_reference': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'fabric': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'style_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'designer': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estimated_duration_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only designer users can be assigned as designer.
        self.fields['designer'].queryset = User.objects.filter(role__code='DESIGNER')
