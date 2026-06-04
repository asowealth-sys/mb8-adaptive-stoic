from __future__ import annotations

import os


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class ProductionSettings:
    api_key: str | None = os.getenv("MB8_API_KEY")
    public_base_url: str = os.getenv("MB8_PUBLIC_BASE_URL", "https://example.onrender.com")
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "MB8_ALLOWED_ORIGINS",
            "https://chatgpt.com,https://chat.openai.com",
        ).split(",")
        if origin.strip()
    ]
    auth_required: bool = env_bool("MB8_AUTH_REQUIRED", default=True)


PRODUCTION_SETTINGS = ProductionSettings()

