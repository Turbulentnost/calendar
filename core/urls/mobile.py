from django.urls import path

from core.views.mobile import mobile_home_background

urlpatterns = [
    path("api/mobile/home-background/", mobile_home_background, name="mobile-home-background"),
]
