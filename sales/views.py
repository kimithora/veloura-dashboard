from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction as db_transaction

from core.mixins import RoleRequiredMixin
from .models import Transaction, TransactionItem
from .service import TransactionService, InsufficientStockError
from .invoice import invoice_pdf
from catalog.models import ProductVariant


def _get_cart(request):
    return request.session.get('cart', [])


def _set_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


@login_required
def pos(request):
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        messages.error(request, 'Only cashiers and admins can use the point of sale.')
        return redirect('core:dashboard')
    cart = _get_cart(request)
    enriched = []
    for item in cart:
        try:
            v = ProductVariant.objects.select_related('product').get(pk=item['variant_id'])
            enriched.append({
                'variant_id': v.pk,
                'sku': v.sku,
                'barcode': v.barcode,
                'name': v.product.name,
                'size': v.get_size_display(),
                'color': v.color,
                'quantity': item['quantity'],
                'unit_price': str(v.effective_selling_price),
                'discount': str(item.get('discount', 0)),
                'total': str((v.effective_selling_price * item['quantity']) - Decimal(str(item.get('discount', 0) or 0))),
                'stock': v.stock_quantity,
                'is_active': v.is_active and v.product.status == 'ACTIVE',
            })
        except ProductVariant.DoesNotExist:
            continue
    grand_total = sum(float(i['unit_price']) * i['quantity'] - float(i['discount']) for i in enriched)
    from customers.models import Customer
    customers = Customer.objects.all().order_by('full_name')
    return render(request, 'sales/pos.html', {
        'title': 'Point of Sale',
        'cart': enriched,
        'grand_total': grand_total,
        'customers': customers,
    })


@require_POST
@login_required
def cart_add(request):
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    variant_id = request.POST.get('variant_id')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Quantity must be a valid number'}, status=400)
    if quantity < 1:
        return JsonResponse({'error': 'Quantity must be at least 1'}, status=400)
    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    if not variant.is_active or variant.product.status != 'ACTIVE':
        return JsonResponse({'error': 'Product is not active'}, status=400)
    if variant.stock_quantity < quantity:
        return JsonResponse({
            'error': 'Insufficient stock: available {}'.format(variant.stock_quantity)
        }, status=400)
    cart = _get_cart(request)
    current_qty = 0
    for item in cart:
        if item['variant_id'] == variant.pk:
            current_qty = int(item.get('quantity', 1))
            break
    if current_qty + quantity > variant.stock_quantity:
        return JsonResponse({
            'error': 'Insufficient stock: available {} (already {} in cart)'.format(
                variant.stock_quantity, current_qty
            )
        }, status=400)
    for item in cart:
        if item['variant_id'] == variant.pk:
            item['quantity'] = current_qty + quantity
            _set_cart(request, cart)
            return JsonResponse({'ok': True, 'cart_count': len(cart)})
    cart.append({
        'variant_id': variant.pk,
        'quantity': quantity,
        'unit_price': str(variant.effective_selling_price),
        'discount': '0',
    })
    _set_cart(request, cart)
    return JsonResponse({'ok': True, 'cart_count': len(cart)})


@require_POST
@login_required
def cart_remove(request):
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    try:
        variant_id = int(request.POST.get('variant_id'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid variant_id'}, status=400)
    cart = _get_cart(request)
    cart = [i for i in cart if i['variant_id'] != variant_id]
    _set_cart(request, cart)
    return JsonResponse({'ok': True})


@require_POST
@login_required
def cart_clear(request):
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    request.session['cart'] = []
    request.session.modified = True
    return JsonResponse({'ok': True})


@login_required
def barcode_lookup(request):
    barcode = request.GET.get('barcode', '').strip()
    if not barcode:
        return JsonResponse({'error': 'Barcode required'}, status=400)
    try:
        variant = ProductVariant.objects.select_related('product').get(barcode=barcode)
    except ProductVariant.DoesNotExist:
        return JsonResponse({'error': 'Barcode not found'}, status=404)
    if not variant.is_active or variant.product.status != 'ACTIVE':
        return JsonResponse({'error': 'Product is not active'}, status=400)
    return JsonResponse({
        'ok': True,
        'variant_id': variant.pk,
        'sku': variant.sku,
        'barcode': variant.barcode,
        'name': variant.product.name,
        'size': variant.get_size_display(),
        'color': variant.color,
        'selling_price': str(variant.effective_selling_price),
        'stock': variant.stock_quantity,
        'is_active': True,
    })


@login_required
@require_POST
def checkout(request):
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    cart = _get_cart(request)
    if not cart:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    customer_id = request.POST.get('customer_id') or None
    discount_amount = request.POST.get('discount_amount') or 0
    discount_type = request.POST.get('discount_type') or 'nominal'
    notes = request.POST.get('notes', 'POS sale')
    amount = request.POST.get('amount') or 0
    method = request.POST.get('method') or 'CASH'
    payment_type = request.POST.get('payment_type') or 'FULL'

    customer = None
    if customer_id:
        from customers.models import Customer
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            customer = None

    # Hitung subtotal dari cart
    subtotal = Decimal('0')
    for item in cart:
        subtotal += Decimal(str(item.get('unit_price', 0))) * int(item.get('quantity', 1))

    # Hitung discount otomatis berdasarkan tipe
    try:
        discount_amount = Decimal(str(discount_amount or 0))
    except Exception:
        discount_amount = Decimal('0')

    if discount_type == 'persen' and subtotal > 0:
        discount_amount = (subtotal * discount_amount / Decimal('100'))
    elif discount_type == 'nominal':
        discount_amount = discount_amount
    else:
        discount_amount = Decimal('0')

    if discount_amount < 0:
        discount_amount = Decimal('0')
    if discount_amount > subtotal:
        discount_amount = subtotal

    try:
        amount = Decimal(str(amount or 0))
    except Exception:
        amount = Decimal('0')
    if amount <= 0:
        amount = None

    try:
        from payments.models import Payment
        with db_transaction.atomic():
            tx = TransactionService.finalize_transaction(
                cart_items=cart,
                cashier=request.user,
                customer=customer,
                discount_amount=discount_amount,
                notes=notes,
            )
            # Catat pembayaran yang dipilih kasir pada modal POS.
            if amount:
                payment = Payment.objects.create(
                    transaction=tx,
                    amount=amount,
                    payment_type=payment_type,
                    method=method,
                    status=Payment.Status.PENDING,
                    notes='POS checkout',
                )
                if request.FILES.get('payment_proof'):
                    payment.payment_proof = request.FILES['payment_proof']
                    payment.save(update_fields=['payment_proof', 'updated_at'])
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    request.session['cart'] = []
    request.session.modified = True
    return JsonResponse({
        'ok': True,
        'transaction_number': tx.transaction_number,
        'grand_total': str(tx.grand_total),
        'url': reverse('sales:transaction_detail', kwargs={'pk': tx.pk}),
    })


@login_required
@require_POST
def cancel_transaction(request, pk):
    """Batalkan transaksi dan kembalikan stok jika sudah dikurangi."""
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    tx = get_object_or_404(Transaction, pk=pk)
    try:
        with db_transaction.atomic():
            TransactionService.cancel_transaction(tx, request.user)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    messages.success(request, 'Transaksi dibatalkan dan stok dikembalikan.')
    return JsonResponse({'ok': True, 'status': tx.status})


class TransactionListView(RoleRequiredMixin, ListView):
    required_roles = ('ADMIN', 'CASHIER')
    template_name = 'catalog/list.html'
    context_object_name = 'transactions'
    paginate_by = 25

    def get_queryset(self):
        qs = Transaction.objects.select_related('customer', 'cashier').all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(transaction_number__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx.update({
            'title': 'Sales Transactions',
            'subtitle': 'View and manage sales transactions',
            'icon': 'shopping-bag',
            'object_list': qs,
            'columns': [
                {'header': 'Transaction #', 'field': 'transaction_number'},
                {'header': 'Customer', 'field': 'customer.full_name'},
                {'header': 'Cashier', 'field': 'cashier.username'},
                {'header': 'Date', 'field': 'transaction_date'},
                {'header': 'Grand Total', 'field': 'grand_total'},
                {'header': 'Payment', 'field': 'get_payment_status_display'},
                {'header': 'Status', 'field': 'get_status_display'},
            ],
            'create_url': 'sales:pos',
            'create_label': 'New Sale',
            'detail_url': 'sales:transaction_detail',
            'empty_message': 'No transactions found.',
            'query': self.request.GET.get('q', ''),
        })
        return ctx


class TransactionDetailView(RoleRequiredMixin, DetailView):
    required_roles = ('ADMIN', 'CASHIER')
    model = Transaction
    template_name = 'sales/transaction_detail.html'
    context_object_name = 'transaction'
