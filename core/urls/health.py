from django.urls import path

from core.views.health import health

urlpatterns = [
    path("health/", health, name="health"),
]
