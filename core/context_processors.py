"""
Template context processors for the VELOURA application.
Makes branding and user role information available in all templates.
"""

from django.conf import settings


def veloura_context(request):
    """
    Inject Veloura branding and current user role into every template context.
    """
    ctx = {
        'VELOURA_SITE_NAME': getattr(settings, 'VELOURA_SITE_NAME', 'VELOURA'),
        'VELOURA_SITE_TAGLINE': getattr(settings, 'VELOURA_SITE_TAGLINE', 'Fashion Management System'),
        'VELOURA_CURRENCY_SYMBOL': getattr(settings, 'VELOURA_CURRENCY_SYMBOL', 'Rp'),
    }
    if request.user.is_authenticated:
        try:
            ctx['user_role'] = request.user.role.name if request.user.role else None
            ctx['user_role_code'] = request.user.role.code if request.user.role else None
        except Exception:
            ctx['user_role'] = None
            ctx['user_role_code'] = None
    else:
        ctx['user_role'] = None
        ctx['user_role_code'] = None
    return ctx
