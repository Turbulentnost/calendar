from django.http import HttpResponse

from core.services.health import health_body


def health(request):
    return HttpResponse(health_body(), content_type="text/plain")
