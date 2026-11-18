from django import forms
from .models import Payment, OrderPayment


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


class OrderPaymentRecordForm(forms.ModelForm):
    payment_type = forms.ChoiceField(
        choices=OrderPayment.PaymentType.choices,
        initial='DP',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = OrderPayment
        fields = ['amount', 'payment_type', 'method', 'due_date', 'payment_proof', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'method': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_proof': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
