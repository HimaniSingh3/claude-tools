from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from claude_tools.config import Settings


class ClientError(RuntimeError):
    """Raised when the Anthropic client cannot be used."""


@dataclass(slots=True)
class ClaudeResponse:
    text: str
    model: str | None = None
    stop_reason: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    message_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "model": self.model,
            "stop_reason": self.stop_reason,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "message_id": self.message_id,
        }


class ClaudeToolsClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ClientError(
                "The 'anthropic' package is not installed. Run: pip install -e ."
            ) from exc

        self.client = Anthropic(api_key=settings.api_key)

    def ask(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> ClaudeResponse:
        payload: dict[str, Any] = {
            "model": model or self.settings.model,
            "max_tokens": max_tokens or self.settings.max_tokens,
            "system": system_prompt or self.settings.system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }
        if temperature is not None:
            payload["temperature"] = temperature

        try:
            response = self.client.messages.create(**payload)
        except Exception as exc:  # noqa: BLE001
            raise ClientError(f"Anthropic API request failed: {exc}") from exc

        text_parts: list[str] = []
        for block in getattr(response, "content", []):
            text = getattr(block, "text", None)
            if text:
                text_parts.append(text)

        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "input_tokens", None) if usage else None
        output_tokens = getattr(usage, "output_tokens", None) if usage else None

        return ClaudeResponse(
            text="\n".join(text_parts).strip(),
            model=getattr(response, "model", None),
            stop_reason=getattr(response, "stop_reason", None),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            message_id=getattr(response, "id", None),
        )
