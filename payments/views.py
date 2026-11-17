from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction as db_transaction
from django.db.models import Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator

from sales.models import Transaction
from sales.service import TransactionService, InsufficientStockError
from inventory.models import StockMovement
from catalog.models import ProductVariant
from django.contrib.contenttypes.models import ContentType
from .models import Payment
from .forms import PaymentRecordForm


def _cashier_or_admin_required(request):
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        return False
    return True


@login_required
@require_POST
def record_payment(request, transaction_pk):
    tx = get_object_or_404(Transaction, pk=transaction_pk)
    if not _cashier_or_admin_required(request):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    form = PaymentRecordForm(request.POST, request.FILES)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.transaction = tx
        payment.status = Payment.Status.PENDING
        payment.save()
        messages.success(request, 'Pembayaran dicatat. Menunggu konfirmasi.')
        return JsonResponse({'ok': True, 'payment_id': payment.pk})
    return JsonResponse({'error': form.errors.as_json()}, status=400)


@login_required
@require_POST
def confirm_payment(request, payment_pk):
    payment = get_object_or_404(Payment, pk=payment_pk)
    tx = payment.transaction
    if not _cashier_or_admin_required(request):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if payment.status != Payment.Status.PENDING:
        return JsonResponse({'error': 'Pembayaran sudah diproses'}, status=400)

    try:
        with db_transaction.atomic():
            # Lock payment and transaction rows to prevent double confirmation (race condition).
            payment = Payment.objects.select_for_update().get(pk=payment_pk)
            tx = Transaction.objects.select_for_update().get(pk=tx.pk)
            if payment.status != Payment.Status.PENDING:
                return JsonResponse({'error': 'Pembayaran sudah diproses'}, status=400)

            confirmed_total = Payment.objects.filter(
                transaction=tx, status=Payment.Status.CONFIRMED
            ).aggregate(total=Sum('amount'))['total'] or 0
            new_total = confirmed_total + payment.amount

            if new_total >= tx.grand_total:
                target_payment = Transaction.PaymentStatus.PAID
                target_status = Transaction.Status.COMPLETED
            else:
                target_payment = Transaction.PaymentStatus.PARTIALLY_PAID
                target_status = Transaction.Status.PENDING

            tx.payment_status = target_payment
            tx.status = target_status
            tx.save(update_fields=['payment_status', 'status', 'updated_at'])

            if target_payment == Transaction.PaymentStatus.PAID:
                TransactionService.deduct_stock(tx, request.user)

            payment.status = Payment.Status.CONFIRMED
            payment.confirmed_at = timezone.now()
            payment.confirmed_by = request.user
            payment.save(update_fields=['status', 'confirmed_at', 'confirmed_by', 'updated_at'])
    except InsufficientStockError as e:
        tx.payment_status = Transaction.PaymentStatus.UNPAID
        tx.status = Transaction.Status.PENDING
        tx.save(update_fields=['payment_status', 'status', 'updated_at'])
        return JsonResponse({'error': str(e)}, status=400)

    messages.success(request, 'Pembayaran dikonfirmasi. Stok telah dikurangi.')
    return JsonResponse({'ok': True, 'payment_status': tx.payment_status, 'status': tx.status})


@login_required
@require_POST
def void_payment(request, payment_pk):
    """Batalkan/tolak pembayaran yang masih pending, atau refund yang sudah confirmed."""
    payment = get_object_or_404(Payment, pk=payment_pk)
    tx = payment.transaction
    if not _cashier_or_admin_required(request):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    with db_transaction.atomic():
        # Lock rows to prevent concurrent void/double refund.
        payment = Payment.objects.select_for_update().get(pk=payment_pk)
        tx = Transaction.objects.select_for_update().get(pk=tx.pk)

        if payment.status == Payment.Status.PENDING:
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=['status', 'updated_at'])
            messages.success(request, 'Pembayaran pending dibatalkan.')
        elif payment.status == Payment.Status.CONFIRMED:
            payment.status = Payment.Status.REFUNDED
            payment.save(update_fields=['status', 'updated_at'])

            # Hitung ulang status transaksi dari pembayaran confirmed yang tersisa.
            confirmed_total = Payment.objects.filter(
                transaction=tx, status=Payment.Status.CONFIRMED
            ).aggregate(total=Sum('amount'))['total'] or 0

            if confirmed_total <= 0:
                new_payment_status = Transaction.PaymentStatus.UNPAID
                new_status = Transaction.Status.PENDING
            elif confirmed_total < tx.grand_total:
                new_payment_status = Transaction.PaymentStatus.PARTIALLY_PAID
                new_status = Transaction.Status.PENDING
            else:
                new_payment_status = Transaction.PaymentStatus.PAID
                new_status = Transaction.Status.COMPLETED

            # Jika stok sudah dipotong sebelumnya tetapi sisa pembayaran tidak
            # lagi mencakup total, kembalikan stok agar inventori tidak menyelisihi
            # status pembayaran. Jika sisa mencukupi, transaksi tetap PAID/COMPLETED
            # dan stok tidak dikembalikan berlebih.
            if tx.stock_deducted and new_status != Transaction.Status.COMPLETED:
                items = tx.items.select_related('product_variant').all()
                variant_ids = [i.product_variant_id for i in items]
                locked = {v.pk: v for v in ProductVariant.objects.select_for_update().filter(pk__in=variant_ids)}
                for item in items:
                    variant = locked.get(item.product_variant_id)
                    if variant is None:
                        continue
                    previous = variant.stock_quantity
                    new_stock = previous + item.quantity
                    variant.stock_quantity = new_stock
                    variant.save(update_fields=['stock_quantity', 'updated_at'])
                    StockMovement.objects.create(
                        content_type=ContentType.objects.get_for_model(ProductVariant),
                        object_id=variant.pk,
                        movement_type=StockMovement.MovementType.RETURN,
                        quantity=item.quantity,
                        previous_stock=previous,
                        new_stock=new_stock,
                        reference=tx.transaction_number,
                        user=request.user,
                        notes='Return for refunded sale {}'.format(tx.transaction_number),
                    )
                tx.stock_deducted = False

            tx.payment_status = new_payment_status
            tx.status = new_status
            tx.save(update_fields=['payment_status', 'status', 'stock_deducted', 'updated_at'])
            messages.success(request, 'Pembayaran dikembalikan (refund).')
        else:
            return JsonResponse({'error': 'Tidak dapat membatalkan pembayaran ini.'}, status=400)

    return JsonResponse({'ok': True})


@login_required
def payment_list(request):
    if not _cashier_or_admin_required(request):
        messages.error(request, 'Tidak diizinkan.')
        return redirect('core:dashboard')

    qs = Payment.objects.select_related('transaction', 'confirmed_by').all()

    # Filters
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    method = request.GET.get('method', '')
    payment_type = request.GET.get('payment_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if q:
        qs = qs.filter(
            Q(transaction__transaction_number__icontains=q) |
            Q(confirmed_by__username__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    if method:
        qs = qs.filter(method=method)
    if payment_type:
        qs = qs.filter(payment_type=payment_type)
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Summary
    confirmed_total = qs.filter(status='CONFIRMED').aggregate(total=Sum('amount'))['total'] or 0
    pending_total = qs.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'title': 'Pembayaran',
        'subtitle': 'Histori dan konfirmasi pembayaran',
        'payments': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'confirmed_total': confirmed_total,
        'pending_total': pending_total,
        'query': q,
        'current_filters': {
            'status': status,
            'method': method,
            'payment_type': payment_type,
            'date_from': date_from,
            'date_to': date_to,
        },
        'status_choices': Payment.Status.choices,
        'method_choices': Payment.Method.choices,
        'payment_type_choices': Payment.PaymentType.choices,
    }
    return render(request, 'payments/payment_list.html', context)


@login_required
def payment_detail(request, payment_pk):
    payment = get_object_or_404(
        Payment.objects.select_related('transaction', 'confirmed_by'), pk=payment_pk
    )
    if not _cashier_or_admin_required(request):
        messages.error(request, 'Tidak diizinkan.')
        return redirect('core:dashboard')
    return render(request, 'payments/payment_detail.html', {
        'title': 'Detail Pembayaran',
        'payment': payment,
    })


@login_required
def transaction_payments(request, transaction_pk):
    """Daftar semua pembayaran untuk satu transaksi."""
    tx = get_object_or_404(Transaction.objects.select_related('customer', 'cashier'), pk=transaction_pk)
    if not _cashier_or_admin_required(request):
        messages.error(request, 'Tidak diizinkan.')
        return redirect('core:dashboard')
    payments = tx.payments.all().select_related('confirmed_by')
    return render(request, 'payments/transaction_payments.html', {
        'title': 'Pembayaran Transaksi',
        'transaction': tx,
        'payments': payments,
    })
