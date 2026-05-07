from django.urls import include, path

urlpatterns = [
    path("", include("core.urls.health")),
    path("", include("core.urls.mobile")),
]
