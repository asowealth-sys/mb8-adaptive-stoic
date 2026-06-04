from __future__ import annotations

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.production_config import PRODUCTION_SETTINGS

API_KEY_HEADER = "X-MB8-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_HEADER, auto_error=False)


def require_api_key(api_key: str | None = Security(api_key_header)) -> None:
    if not PRODUCTION_SETTINGS.auth_required:
        return
    expected = PRODUCTION_SETTINGS.api_key
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MB8_API_KEY is not configured.",
        )
    if api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing MB 8.0 API key.",
        )

