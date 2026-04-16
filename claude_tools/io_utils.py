from __future__ import annotations

import sys
from pathlib import Path


class InputError(ValueError):
    """Raised when user input cannot be loaded."""


def read_stdin_text() -> str:
    return sys.stdin.read().strip()


def read_text_file(path: str | Path) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise InputError(f"File not found: {file_path}")
    if not file_path.is_file():
        raise InputError(f"Not a file: {file_path}")
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="utf-8", errors="replace")


def write_text_file(path: str | Path, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")
