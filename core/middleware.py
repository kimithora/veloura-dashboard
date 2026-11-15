"""
Middleware for VELOURA role-based access handling.

RoleRedirectMiddleware redirects users to their role-appropriate dashboard
when they land on the root URL or an unauthorized home path.
"""

from django.shortcuts import redirect
from django.urls import reverse


class RoleRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Only apply to authenticated users on the root path
        if not request.user.is_authenticated:
            return None
        if request.path in ('/', reverse('core:dashboard',)) or request.path == '/':
            role = getattr(request.user, 'role', None)
            if role is None:
                return None
            code = role.code
            if code == 'ADMIN':
                return redirect('core:admin_dashboard')
            if code == 'CASHIER':
                return redirect('core:cashier_dashboard')
            if code == 'DESIGNER':
                return redirect('core:designer_dashboard')
        return None
