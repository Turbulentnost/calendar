from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404


def mobile_home_background(request):
    candidates = (
        Path(settings.MEDIA_ROOT) / "mobile" / "главная.png",
        Path(settings.MEDIA_ROOT) / "mobile" / "главная.png",
    )
    for image_path in candidates:
        if image_path.exists():
            return FileResponse(open(image_path, "rb"), content_type="image/png")
    raise Http404("Фоновое изображение не найдено.")
