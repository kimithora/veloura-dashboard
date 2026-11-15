"""
Authorization mixins for class-based views.
"""

from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin


class RoleRequiredMixin(LoginRequiredMixin):
    """
    CBV mixin: require the user to have one of the given role codes.
    Usage: class MyView(RoleRequiredMixin(['ADMIN', 'CASHIER']), View): ...
    """
    required_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        role = getattr(request.user, 'role', None)
        if role is None or role.code not in self.required_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        from django.shortcuts import render
        from django.http import HttpRequest
        # Return 403 for authenticated but unauthorized
        if self.request.user.is_authenticated:
            return render(self.request, 'core/403.html', status=403)
        return super().handle_no_permission()


class StaffOrAdminMixin(RoleRequiredMixin):
    required_roles = ('ADMIN', 'CASHIER', 'DESIGNER')
