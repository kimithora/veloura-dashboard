"""
Core views for the VELOURA Fashion Management System.

Provides the base dashboards for Admin, Cashier, and Designer roles.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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
    """Admin dashboard overview."""
    return render(request, 'core/admin_dashboard.html')


@login_required
@role_required('CASHIER')
def cashier_dashboard(request):
    """Cashier dashboard overview."""
    return render(request, 'core/cashier_dashboard.html')


@login_required
@role_required('DESIGNER')
def designer_dashboard(request):
    """Designer dashboard overview."""
    return render(request, 'core/designer_dashboard.html')


@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint."""
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok', 'site': 'VELOURA'})
