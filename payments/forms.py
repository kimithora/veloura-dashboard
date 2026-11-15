from django import forms
from .models import Payment


class PaymentRecordForm(forms.ModelForm):
    payment_type = forms.ChoiceField(
        choices=Payment.PaymentType.choices,
        initial='FULL',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Payment
        fields = ['amount', 'payment_type', 'method', 'due_date', 'payment_proof']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'method': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_proof': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
