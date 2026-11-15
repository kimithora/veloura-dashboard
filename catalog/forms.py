from django import forms
from .models import Brand, Category, Product, ProductVariant, Barcode


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku', 'name', 'description', 'category', 'brand', 'source',
            'supplier', 'purchase_price', 'selling_price', 'min_stock',
            'image', 'status',
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        source = cleaned.get('source')
        supplier = cleaned.get('supplier')
        if source in ('THIRD_PURCHASED', 'THIRD_CONSIGNMENT') and not supplier:
            self.add_error('supplier', 'A supplier is required for third-party products.')
        return cleaned


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['sku', 'barcode', 'size', 'color', 'stock_quantity', 'selling_price', 'purchase_price', 'is_active']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'size': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        if product:
            self.fields['sku'].initial = product.sku + '-VAR'

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        qs = ProductVariant.objects.filter(sku=sku)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('This SKU already exists.')
        return sku

    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode')
        if barcode:
            qs = ProductVariant.objects.filter(barcode=barcode)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('This barcode already exists.')
        return barcode


class CustomBarcodeForm(forms.Form):
    """
    Form untuk membuat kode barcode sendiri (manual) dan langsung
    menambah stok (stock-in) saat mencetak label.
    """
    barcode_value = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 8901234567890'}),
        help_text='Masukkan kode barcode sendiri. Harus unik.'
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        help_text='Jumlah stok yang akan ditambah.'
    )
    label_format = forms.ChoiceField(
        choices=[('png', 'PNG'), ('pdf', 'PDF')],
        initial='png',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def clean_barcode_value(self):
        value = self.cleaned_data.get('barcode_value')
        if value and ProductVariant.objects.filter(barcode=value).exists():
            raise forms.ValidationError('Kode barcode sudah digunakan oleh variant lain.')
        if value and Barcode.objects.filter(barcode_value=value).exists():
            raise forms.ValidationError('Kode barcode sudah terdaftar.')
        return value
