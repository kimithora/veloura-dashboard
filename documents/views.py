from django.http import HttpResponse


def index(request):
    """Placeholder for the documents module (future feature)."""
    return HttpResponse(
        '<h2>documents Module</h2><p>This module is planned for a future development phase.</p>'
        '<a href="/">Back to Dashboard</a>',
        content_type='text/html',
    )
