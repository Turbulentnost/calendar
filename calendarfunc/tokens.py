import base64
import hashlib
import hmac
import json
import time

from django.conf import settings


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def create_project_token(project) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "type": "project",
        "project_id": project.pk,
        "login": project.login,
        "iat": int(time.time()),
    }
    signing_input = ".".join(
        [
            _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64encode(signature)}"


def decode_project_token(token: str) -> dict:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise ValueError("Неверный токен проекта.") from exc

    signing_input = f"{header_b64}.{payload_b64}"
    expected = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(_b64encode(expected), signature_b64):
        raise ValueError("Неверная подпись токена проекта.")

    payload = json.loads(_b64decode(payload_b64))
    if payload.get("type") != "project" or not payload.get("project_id"):
        raise ValueError("Неверный токен проекта.")
    return payload
