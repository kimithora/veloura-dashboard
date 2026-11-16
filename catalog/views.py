"""
Catalogue views (Phase 2): Brand, Category, Product, ProductVariant, Barcode.
Uses shared templates (list.html, form.html, confirm_*.html).
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse

from core.mixins import RoleRequiredMixin
from .models import Brand, Category, Product, ProductVariant, Barcode
from .forms import BrandForm, CategoryForm, ProductForm, ProductVariantForm, CustomBarcodeForm

import barcode
from barcode.writer import ImageWriter
from PIL import Image
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.db import transaction as db_transaction
from django.contrib.contenttypes.models import ContentType
from inventory.models import StockMovement
from django.utils import timezone


def list_context(title, subtitle, icon, object_list, columns, create_url=None,
                 create_label='Add New', edit_url=None, detail_url=None,
                 delete_url=None, archive_url=None, filters=None, empty_message=None,
                 request=None):
    ctx = {
        'title': title,
        'subtitle': subtitle,
        'icon': icon,
        'object_list': object_list,
        'columns': columns,
        'create_url': reverse_lazy(create_url) if create_url else None,
        'create_label': create_label,
        'edit_url': edit_url,
        'detail_url': detail_url,
        'delete_url': delete_url,
        'archive_url': archive_url,
        'filters': filters or [],
        'empty_message': empty_message,
        'query': request.GET.get('q', '') if request else '',
        'current_filters': {k: v for k, v in (request.GET.items() if request else []) if k not in ('q', 'page')},
    }
    return ctx


# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------
class BrandListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    template_name = 'catalog/list.html'
    context_object_name = 'brands'
    paginate_by = 20

    def get_queryset(self):
        qs = Brand.objects.all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update(list_context(
            'Brands', 'Manage product brands', 'layout',
            qs,
            [
                {'header': 'Name', 'field': 'name'},
                {'header': 'Slug', 'field': 'slug'},
                {'header': 'Products', 'field': 'products.count', 'detail_url': None},
            ],
            create_url='catalog:brand_add',
            edit_url='catalog:brand_edit',
            delete_url='catalog:brand_delete',
            filters=[('q', 'Search', [])],
            empty_message='No brands found.',
            request=self.request,
        ))
        return ctx


class BrandCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Brand
    form_class = BrandForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('catalog:brand_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add Brand'
        ctx['subtitle'] = 'Create a new product brand'
        ctx['icon'] = 'tag'
        ctx['cancel_url'] = reverse_lazy('catalog:brand_list')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Brand created successfully.')
        return super().form_valid(form)


class BrandUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Brand
    form_class = BrandForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('catalog:brand_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Brand'
        ctx['subtitle'] = 'Update brand details'
        ctx['icon'] = 'edit-2'
        ctx['cancel_url'] = reverse_lazy('catalog:brand_list')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Brand updated successfully.')
        return super().form_valid(form)


class BrandDeleteView(RoleRequiredMixin, DeleteView):
    required_roles = ('ADMIN',)
    model = Brand
    template_name = 'catalog/confirm_delete.html'
    success_url = reverse_lazy('catalog:brand_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Delete Brand'
        ctx['subtitle'] = 'Remove this brand'
        ctx['object_name'] = 'Brand'
        ctx['object'] = self.object.name
        ctx['cancel_url'] = reverse_lazy('catalog:brand_list')
        return ctx


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------
class CategoryListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    template_name = 'catalog/list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        qs = Category.objects.all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update(list_context(
            'Categories', 'Manage product categories', 'layout-list',
            qs,
            [
                {'header': 'Name', 'field': 'name'},
                {'header': 'Slug', 'field': 'slug'},
            ],
            create_url='catalog:category_add',
            edit_url='catalog:category_edit',
            delete_url='catalog:category_delete',
            empty_message='No categories found.',
            request=self.request,
        ))
        return ctx


class CategoryCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Category
    form_class = CategoryForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('catalog:category_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add Category'
        ctx['subtitle'] = 'Create a new product category'
        ctx['icon'] = 'folder'
        ctx['cancel_url'] = reverse_lazy('catalog:category_list')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully.')
        return super().form_valid(form)


class CategoryUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Category
    form_class = CategoryForm
    template_name = 'catalog/form.html'
    success_url = reverse_lazy('catalog:category_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Category'
        ctx['subtitle'] = 'Update category details'
        ctx['icon'] = 'edit-2'
        ctx['cancel_url'] = reverse_lazy('catalog:category_list')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully.')
        return super().form_valid(form)


class CategoryDeleteView(RoleRequiredMixin, DeleteView):
    required_roles = ('ADMIN',)
    model = Category
    template_name = 'catalog/confirm_delete.html'
    success_url = reverse_lazy('catalog:category_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Delete Category'
        ctx['subtitle'] = 'Remove this category'
        ctx['object_name'] = 'Category'
        ctx['object'] = self.object.name
        ctx['cancel_url'] = reverse_lazy('catalog:category_list')
        return ctx


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------
class ProductListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    template_name = 'catalog/list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.select_related('category', 'brand', 'supplier').all()
        q = self.request.GET.get('q')
        source = self.request.GET.get('source')
        status = self.request.GET.get('status')
        if q:
            qs = qs.filter(sku__icontains=q)
            if not qs:
                qs = Product.objects.filter(name__icontains=q)
        if source:
            qs = qs.filter(source=source)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update(list_context(
            'Products', 'Manage the product catalogue', 'tag',
            qs,
            [
                {'header': 'SKU', 'field': 'sku'},
                {'header': 'Name', 'field': 'name'},
                {'header': 'Category', 'field': 'category.name'},
                {'header': 'Source', 'field': 'get_source_display'},
                {'header': 'Status', 'field': 'get_status_display'},
                {'header': 'Selling Price', 'field': 'selling_price'},
                {'header': 'Stock', 'field': 'total_stock'},
            ],
            create_url='catalog:product_add',
            detail_url='catalog:product_detail',
            edit_url='catalog:product_edit',
            archive_url='catalog:product_archive',
            filters=[
                ('source', 'Source', Product.Source.choices),
                ('status', 'Status', Product.Status.choices),
            ],
            empty_message='No products found.',
            request=self.request,
        ))
        return ctx


class ProductDetailView(RoleRequiredMixin, DetailView):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Product
    form_class = ProductForm
    template_name = 'catalog/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add Product'
        ctx['subtitle'] = 'Create a new product'
        ctx['icon'] = 'package'
        ctx['cancel_url'] = reverse_lazy('catalog:product_list')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('catalog:product_detail', kwargs={'pk': self.object.pk})


class ProductUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Product
    form_class = ProductForm
    template_name = 'catalog/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Product'
        ctx['subtitle'] = 'Update product details'
        ctx['icon'] = 'edit-2'
        ctx['cancel_url'] = reverse('catalog:product_detail', kwargs={'pk': self.object.pk})
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('catalog:product_detail', kwargs={'pk': self.object.pk})


class ProductArchiveView(RoleRequiredMixin, DeleteView):
    """
    Archive a product (set status ARCHIVED) rather than hard delete, to keep
    historical records intact.
    """
    required_roles = ('ADMIN',)
    model = Product
    template_name = 'catalog/confirm_archive.html'
    success_url = reverse_lazy('catalog:product_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Archive Product'
        ctx['subtitle'] = 'Archive this product'
        ctx['object_name'] = 'Product'
        ctx['object'] = self.object.name
        ctx['cancel_url'] = reverse_lazy('catalog:product_list')
        return ctx

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        product.status = Product.Status.ARCHIVED
        product.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Product archived. Historical records are preserved.')
        return redirect(self.success_url)


# ---------------------------------------------------------------------------
# Product Variant
# ---------------------------------------------------------------------------
class ProductVariantCreateView(RoleRequiredMixin, CreateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = ProductVariant
    form_class = ProductVariantForm
    template_name = 'catalog/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=kwargs['product_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = self.product
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add Variant'
        ctx['subtitle'] = 'Add a size/color variant for {}'.format(self.product.name)
        ctx['icon'] = 'layers'
        ctx['cancel_url'] = reverse('catalog:product_detail', kwargs={'pk': self.product.pk})
        return ctx

    def form_valid(self, form):
        variant = form.save(commit=False)
        variant.product = self.product
        if not variant.barcode:
            variant.barcode = self._generate_barcode()
        variant.save()
        Barcode.objects.create(
            product_variant=variant,
            barcode_value=variant.barcode,
            format=Barcode.Format.CODE_128,
        )
        messages.success(self.request, 'Variant created. Barcode: {}'.format(variant.barcode))
        return redirect('catalog:product_detail', pk=self.product.pk)

    def _generate_barcode(self):
        import random
        while True:
            code = '890{:010d}'.format(random.randint(0, 9999999999))
            if not ProductVariant.objects.filter(barcode=code).exists():
                return code


class ProductVariantUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ('ADMIN', 'CASHIER')
    model = ProductVariant
    form_class = ProductVariantForm
    template_name = 'catalog/form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Edit Variant'
        ctx['subtitle'] = 'Update variant stock and pricing'
        ctx['icon'] = 'edit-2'
        ctx['cancel_url'] = reverse('catalog:product_detail', kwargs={'pk': self.object.product.pk})
        return ctx

    def form_valid(self, form):
        variant = self.get_object()
        previous_stock = variant.stock_quantity
        response = super().form_valid(form)
        new_stock = variant.stock_quantity
        if new_stock != previous_stock:
            from inventory.models import StockMovement
            from django.contrib.contenttypes.models import ContentType
            StockMovement.objects.create(
                content_type=ContentType.objects.get_for_model(ProductVariant),
                object_id=variant.pk,
                movement_type=StockMovement.MovementType.ADJUSTMENT,
                quantity=abs(new_stock - previous_stock),
                previous_stock=previous_stock,
                new_stock=new_stock,
                reference='VARIANT-EDIT-{}'.format(variant.pk),
                user=self.request.user,
                notes='Manual stock adjustment via variant edit.',
            )
        messages.success(self.request, 'Variant updated successfully. Stock change recorded in ledger.')
        return response


class ProductVariantDeleteView(RoleRequiredMixin, DeleteView):
    required_roles = ('ADMIN',)
    model = ProductVariant
    template_name = 'catalog/confirm_delete.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Delete Variant'
        ctx['subtitle'] = 'Remove this variant'
        ctx['object_name'] = 'Variant'
        ctx['object'] = str(self.object)
        ctx['cancel_url'] = reverse('catalog:product_detail', kwargs={'pk': self.object.product.pk})
        return ctx

    def get_success_url(self):
        return reverse('catalog:product_detail', kwargs={'pk': self.object.product.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Variant deleted.')
        return super().delete(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Barcode
# ---------------------------------------------------------------------------
class BarcodeListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER')
    template_name = 'catalog/list.html'
    context_object_name = 'barcodes'
    paginate_by = 25

    def get_queryset(self):
        return Barcode.objects.select_related('product_variant__product').all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update(list_context(
            'Barcodes', 'Manage barcode identifiers', 'barcode',
            qs,
            [
                {'header': 'Barcode', 'field': 'barcode_value'},
                {'header': 'Format', 'field': 'get_format_display'},
                {'header': 'Variant', 'field': 'product_variant.sku'},
                {'header': 'Product', 'field': 'product_variant.product.name'},
                {'header': 'Active', 'field': 'is_active'},
            ],
            edit_url=None,
            detail_url='catalog:barcode_label_png',
            delete_url=None,
            empty_message='No barcodes found.',
            request=self.request,
        ))
        return ctx


@login_required
def regenerate_barcode(request, pk):
    """Regenerate a barcode (ADMIN authorized)."""
    if not request.user.has_role('ADMIN'):
        messages.error(request, 'Only an administrator can regenerate barcodes.')
        return redirect('catalog:barcode_list')
    barcode = get_object_or_404(Barcode, pk=pk)
    import random
    while True:
        code = '890{:010d}'.format(random.randint(0, 9999999999))
        if not Barcode.objects.filter(barcode_value=code).exists():
            break
    old = barcode.barcode_value
    barcode.barcode_value = code
    barcode.is_active = True
    barcode.save()
    variant = barcode.product_variant
    variant.barcode = code
    variant.save(update_fields=['barcode'])
    messages.success(request, 'Barcode regenerated: {} -> {}'.format(old, code))
    return redirect('catalog:barcode_list')


@login_required
def barcode_label_png(request, barcode_pk):
    """Generate a printable barcode label PNG for a product variant."""
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        return redirect('core:dashboard')
    barcode_obj = get_object_or_404(Barcode, pk=barcode_pk)
    variant = barcode_obj.product_variant
    code = variant.barcode or ''
    if not code:
        messages.error(request, 'This variant has no barcode.')
        return redirect('catalog:product_detail', pk=variant.product.pk)

    code128 = barcode.get_barcode_class('code128')
    buf = io.BytesIO()
    code128(code, writer=ImageWriter()).write(buf, {
        'module_width': 0.45,
        'module_height': 18.0,
        'quiet_zone': 6,
        'font_size': 14,
        'text_distance': 5,
        'background': 'white',
        'foreground': 'black',
    })
    buf.seek(0)
    img = Image.open(buf).convert('RGB')

    # Compose a label with product info.
    label_w, label_h = 420, 220
    label = Image.new('RGB', (label_w, label_h), 'white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(label)
    try:
        font_big = ImageFont.truetype('arial.ttf', 24)
        font_small = ImageFont.truetype('arial.ttf', 16)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
    img.thumbnail((380, 140))
    label.paste(img, ((label_w - img.width) // 2, 30))
    draw.text((label_w // 2, 175), variant.sku, anchor='mt', font=font_small, fill='black')
    draw.text((label_w // 2, 200), code, anchor='mt', font=font_big, fill='black')

    out = io.BytesIO()
    label.save(out, format='PNG')
    out.seek(0)
    response = HttpResponse(out.read(), content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename="label-{}.png"'.format(code)
    return response


@login_required
def barcode_label_pdf(request, barcode_pk):
    """Generate a printable barcode label PDF for a product variant."""
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        return redirect('core:dashboard')
    barcode_obj = get_object_or_404(Barcode, pk=barcode_pk)
    variant = barcode_obj.product_variant
    code = variant.barcode or ''
    if not code:
        messages.error(request, 'This variant has no barcode.')
        return redirect('catalog:product_detail', pk=variant.product.pk)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont('Helvetica-Bold', 16)
    c.drawCentredString(A4[0] / 2, A4[1] - 30 * mm, 'VELOURA — Barcode Label')
    c.setFont('Helvetica', 12)
    c.drawCentredString(A4[0] / 2, A4[1] - 50 * mm, variant.sku)
    c.drawCentredString(A4[0] / 2, A4[1] - 70 * mm, variant.product.name)
    code128 = barcode.get_barcode_class('code128')
    imgbuf = io.BytesIO()
    code128(code, writer=ImageWriter()).write(imgbuf, {
        'module_width': 0.6, 'module_height': 22.0, 'quiet_zone': 8,
        'font_size': 16, 'text_distance': 7,
    })
    imgbuf.seek(0)
    from reportlab.lib.utils import ImageReader
    c.drawImage(ImageReader(imgbuf),
                A4[0] / 2 - 40 * mm, A4[1] - 130 * mm, width=80 * mm, height=25 * mm)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(A4[0] / 2, A4[1] - 150 * mm, code)
    c.showPage()
    c.save()
    buf.seek(0)
    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="label-{}.pdf"'.format(code)
    return response


@login_required
def create_custom_barcode(request, variant_pk):
    """
    Buat kode barcode sendiri (manual), langsung tambah stok (stock-in),
    dan siap untuk dicetak label PNG/PDF.
    """
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        return redirect('core:dashboard')
    variant = get_object_or_404(ProductVariant, pk=variant_pk)

    if request.method == 'POST':
        form = CustomBarcodeForm(request.POST)
        if form.is_valid():
            barcode_value = form.cleaned_data['barcode_value']
            quantity = form.cleaned_data['quantity']
            label_format = form.cleaned_data['label_format']

            with db_transaction.atomic():
                # 1. Simpan barcode ke variant
                variant.barcode = barcode_value
                variant.save(update_fields=['barcode', 'updated_at'])

                # 2. Buat record Barcode
                barcode_obj = Barcode.objects.create(
                    product_variant=variant,
                    barcode_value=barcode_value,
                    format=Barcode.Format.CODE_128,
                    is_active=True,
                )

                # 3. Stock-in (PURCHASE) - stok bertambah
                previous_stock = variant.stock_quantity
                new_stock = previous_stock + quantity
                variant.stock_quantity = new_stock
                variant.save(update_fields=['stock_quantity', 'updated_at'])

                StockMovement.objects.create(
                    content_type=ContentType.objects.get_for_model(ProductVariant),
                    object_id=variant.pk,
                    movement_type=StockMovement.MovementType.PURCHASE,
                    quantity=quantity,
                    previous_stock=previous_stock,
                    new_stock=new_stock,
                    reference='CUSTOM-{}-{}'.format(barcode_value, timezone.localdate().strftime('%Y%m%d')),
                    user=request.user,
                    notes='Custom barcode created & stock-in: {}'.format(barcode_value),
                )

            messages.success(
                request,
                'Barcode {} berhasil dibuat. Stok ditambah {} (total sekarang {}).'.format(
                    barcode_value, quantity, new_stock
                )
            )
            # Generate dan unduh label sesuai format yang dipilih (PNG atau PDF).
            if label_format == 'pdf':
                return redirect('catalog:barcode_label_pdf', barcode_pk=barcode_obj.pk)
            return redirect('catalog:barcode_label_png', barcode_pk=barcode_obj.pk)
    else:
        form = CustomBarcodeForm()

    return render(request, 'catalog/custom_barcode_form.html', {
        'title': 'Create Custom Barcode',
        'subtitle': 'Buat kode barcode sendiri & tambah stok',
        'icon': 'barcode',
        'form': form,
        'variant': variant,
        'cancel_url': reverse('catalog:product_detail', kwargs={'pk': variant.product.pk}),
    })
