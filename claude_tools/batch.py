from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


class BatchError(ValueError):
    """Raised when batch input is invalid."""


@dataclass(slots=True)
class BatchJob:
    name: str
    prompt: str | None = None
    template: str | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    system: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BatchResult:
    name: str
    prompt: str
    response: str
    template: str | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    system: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_batch_jobs(path: str | Path) -> list[BatchJob]:
    file_path = Path(path)
    if not file_path.exists():
        raise BatchError(f"Batch file not found: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".jsonl":
        return _load_jsonl(file_path)
    return _load_json(file_path)


def dump_batch_results(results: list[BatchResult], path: str | Path) -> None:
    payload = [result.to_dict() for result in results]
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_json(path: Path) -> list[BatchJob]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BatchError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, list):
        raise BatchError("JSON batch files must contain a list of jobs.")

    return [_validate_job(item, index=index + 1) for index, item in enumerate(raw)]


def _load_jsonl(path: Path) -> list[BatchJob]:
    jobs: list[BatchJob] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise BatchError(f"Invalid JSONL on line {index} in {path}: {exc}") from exc
        jobs.append(_validate_job(raw, index=index))
    if not jobs:
        raise BatchError("JSONL batch file is empty.")
    return jobs


def _validate_job(item: Any, index: int) -> BatchJob:
    if not isinstance(item, dict):
        raise BatchError(f"Job #{index} must be a JSON object.")

    name = str(item.get("name") or f"job-{index}").strip()
    prompt = item.get("prompt")
    template = item.get("template")
    variables = item.get("variables") or {}
    system = item.get("system")
    metadata = item.get("metadata") or {}

    if prompt is not None and not isinstance(prompt, str):
        raise BatchError(f"Job '{name}' has a non-string prompt.")
    if template is not None and not isinstance(template, str):
        raise BatchError(f"Job '{name}' has a non-string template.")
    if not prompt and not template:
        raise BatchError(f"Job '{name}' must define either 'prompt' or 'template'.")
    if not isinstance(variables, dict):
        raise BatchError(f"Job '{name}' has non-object 'variables'.")
    if system is not None and not isinstance(system, str):
        raise BatchError(f"Job '{name}' has a non-string system prompt.")
    if not isinstance(metadata, dict):
        raise BatchError(f"Job '{name}' has non-object 'metadata'.")

    return BatchJob(
        name=name,
        prompt=prompt,
        template=template,
        variables=variables,
        system=system,
        metadata=metadata,
    )
