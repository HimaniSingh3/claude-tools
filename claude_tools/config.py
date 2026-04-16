from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_SYSTEM_PROMPT = "You are a precise and helpful engineering assistant."


@dataclass(slots=True)
class Settings:
    api_key: str
    model: str = DEFAULT_MODEL
    max_tokens: int = 1500
    system_prompt: str = DEFAULT_SYSTEM_PROMPT


class ConfigError(RuntimeError):
    """Raised when environment configuration is invalid."""


def get_settings(require_api_key: bool = True) -> Settings:
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if require_api_key and not api_key:
        raise ConfigError(
            "ANTHROPIC_API_KEY is missing. Copy .env.example to .env and add your key."
        )

    model = os.getenv("CLAUDE_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

    raw_max_tokens = os.getenv("CLAUDE_MAX_TOKENS", "1500").strip()
    try:
        max_tokens = int(raw_max_tokens)
    except ValueError as exc:
        raise ConfigError("CLAUDE_MAX_TOKENS must be an integer.") from exc

    if max_tokens <= 0:
        raise ConfigError("CLAUDE_MAX_TOKENS must be greater than zero.")

    system_prompt = os.getenv("CLAUDE_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT).strip()
    if not system_prompt:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    return Settings(
        api_key=api_key,
        model=model,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
    )


def redact_api_key(value: str) -> str:
    if not value:
        return "[not set]"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"
