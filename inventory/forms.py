from django import forms
from .models import Material, StockMovement


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'name', 'category', 'unit', 'stock_quantity', 'min_stock',
            'supplier', 'purchase_price', 'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class StockAdjustmentForm(forms.Form):
    movement_type = forms.ChoiceField(
        choices=StockMovement.MovementType.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    quantity = forms.DecimalField(
        min_value=0, max_digits=12, decimal_places=3,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
    )
    reference = forms.CharField(
        required=False, max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    notes = forms.CharField(
        required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )
