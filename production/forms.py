from django import forms
from .models import Production, MaterialRequest, QualityControl


class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = [
            'order', 'designer', 'start_date', 'estimated_completion',
            'actual_completion', 'progress', 'status', 'notes',
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-select'}),
            'designer': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estimated_completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actual_completion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MaterialRequestForm(forms.ModelForm):
    class Meta:
        model = MaterialRequest
        fields = ['production', 'material', 'quantity', 'notes']
        widgets = {
            'production': forms.Select(attrs={'class': 'form-select'}),
            'material': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MaterialRequestActionForm(forms.Form):
    action = forms.ChoiceField(choices=[('approve', 'Approve'), ('fulfill', 'Fulfilled'), ('reject', 'Reject')])
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))


class QualityControlForm(forms.ModelForm):
    class Meta:
        model = QualityControl
        fields = [
            'order', 'stitching_quality', 'size_accuracy', 'fabric_quality',
            'color_consistency', 'design_conformity', 'cleanliness',
            'final_appearance', 'status', 'notes', 'qc_by',
        ]
        widgets = {
            'order': forms.Select(attrs={'class': 'form-select'}),
            'stitching_quality': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'size_accuracy': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fabric_quality': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'color_consistency': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'design_conformity': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cleanliness': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'final_appearance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'qc_by': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
