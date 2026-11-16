"""
Core views for the VELOURA Fashion Management System.

Provides the base dashboards for Admin, Cashier, and Designer roles with
real business statistics.
"""

from datetime import date, timedelta

from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_http_methods


def role_required(*allowed_codes):
    """
    Decorator restricting access to users whose role code is in allowed_codes.
    """
    def decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            role = getattr(request.user, 'role', None)
            if role is None or role.code not in allowed_codes:
                return render(request, 'core/403.html', status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


@login_required
def dashboard(request):
    """Root dashboard: redirect based on role."""
    role = getattr(request.user, 'role', None)
    if role is None:
        return render(request, 'core/403.html', status=403)
    code = role.code
    if code == 'ADMIN':
        return redirect('core:admin_dashboard')
    if code == 'CASHIER':
        return redirect('core:cashier_dashboard')
    if code == 'DESIGNER':
        return redirect('core:designer_dashboard')
    return render(request, 'core/403.html', status=403)


@login_required
@role_required('ADMIN')
def admin_dashboard(request):
    """Admin dashboard overview with real statistics."""
    from accounts.models import User
    from catalog.models import Product, ProductVariant
    from sales.models import Transaction
    from inventory.models import Material

    today = timezone.localdate()
    total_users = User.objects.count()
    total_products = Product.objects.count()
    sales_today = Transaction.objects.filter(transaction_date__date=today).aggregate(
        total=Sum('grand_total')
    )['total'] or 0
    # Low-stock count computed in Python to avoid cross-app F expression issues.
    low_stock_count = sum(
        1 for v in ProductVariant.objects.filter(
            is_active=True, product__status='ACTIVE'
        ).select_related('product')
        if v.stock_quantity <= v.product.min_stock
    )

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'sales_today': sales_today,
        'low_stock_count': low_stock_count,
        'today': today,
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required
@role_required('CASHIER')
def cashier_dashboard(request):
    """Cashier dashboard overview with real statistics."""
    from catalog.models import Product, ProductVariant
    from sales.models import Transaction

    today = timezone.localdate()
    sales_today = Transaction.objects.filter(transaction_date__date=today).aggregate(
        total=Sum('grand_total')
    )['total'] or 0
    transactions_today = Transaction.objects.filter(transaction_date__date=today).count()
    available_products = ProductVariant.objects.filter(
        is_active=True, product__status='ACTIVE', stock_quantity__gt=0
    ).count()
    low_stock_count = sum(
        1 for v in ProductVariant.objects.filter(
            is_active=True, product__status='ACTIVE'
        ).select_related('product')
        if v.stock_quantity <= v.product.min_stock
    )

    context = {
        'sales_today': sales_today,
        'transactions_today': transactions_today,
        'available_products': available_products,
        'low_stock_count': low_stock_count,
        'today': today,
    }
    return render(request, 'core/cashier_dashboard.html', context)


@login_required
@role_required('DESIGNER')
def designer_dashboard(request):
    """Designer dashboard overview with real statistics."""
    from orders.models import Order
    from designs.models import Design
    from production.models import Production, QualityControl

    today = timezone.localdate()
    active_projects = Order.objects.filter(
        status__in=(
            Order.Status.MEASUREMENT, Order.Status.DESIGNING,
            Order.Status.DESIGN_APPROVAL, Order.Status.MATERIAL_PREP,
            Order.Status.PRODUCTION, Order.Status.FITTING, Order.Status.QC,
        )
    ).count()
    pending_designs = Design.objects.filter(status=Design.Status.PENDING_APPROVAL).count()
    production_in_progress = Production.objects.filter(
        status=Production.Status.IN_PROGRESS
    ).count()
    qc_pending = QualityControl.objects.filter(status=QualityControl.Status.PENDING).count()

    context = {
        'active_projects': active_projects,
        'pending_designs': pending_designs,
        'production_in_progress': production_in_progress,
        'qc_pending': qc_pending,
        'today': today,
    }
    return render(request, 'core/designer_dashboard.html', context)


@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok', 'site': 'VELOURA'})
